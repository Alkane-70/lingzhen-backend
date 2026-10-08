import os
import json
from dotenv import load_dotenv, find_dotenv
from zhipuai import ZhipuAI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 导入RAG、图谱和数据库模块
from backend.rag_service import search_medical_context
from backend.graph_service import get_graph_path
from backend.database import SessionLocal, DiagnosisRecord

load_dotenv(find_dotenv())
api_key = os.getenv("ZHIPU_API_KEY")

client = ZhipuAI(api_key=api_key)
app = FastAPI(title="灵诊智库后端")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    symptom: str
    role: str = "patient"
    age: str = "25岁"
    gender: str = "男"

@app.post("/api/diagnose")
async def diagnose(request: QueryRequest):
    symptom = request.symptom
    
    # 1. 获取本地 RAG 文献和知识图谱上下文 
    contexts = search_medical_context(symptom)
    context_str = "\n".join(contexts)
    graph_nodes_local = get_graph_path(symptom)
    graph_str = " -> ".join([node["name"] for node in graph_nodes_local])

    # 2. 根据角色动态生成 Prompt
    if request.role == "doctor":
        system_prompt = f"""你是一个专业的临床辅助诊断系统。
        请根据患者的症状，结合医学文献和知识图谱，给出专业的医疗建议。
        医学文献参考：{context_str}
        图谱路径：{graph_str}
        
        请严格按照以下JSON格式返回结果：
        {{
            "department": "相关科室",
            "confidence": 0.95,
            "reason": "专业医学参考资料摘要，包含鉴别诊断，字数80字以内",
            "graph_nodes": [
                {{"name": "查询对象", "type": "drug"}},
                {{"name": "相关疾病", "type": "disease"}},
                {{"name": "适应症", "type": "symptom"}},
                {{"name": "相关科室", "type": "department"}}
            ]
        }}
        注意：
        1. type 只能是 symptom(症状), disease(疾病), department(科室), drug(药物/文献) 这四种。
        2. 如果用户问的是药物，请把药物作为 "drug" 类型。
        3. 只返回JSON，绝对不要有任何其他解释文字。"""
    else:
        system_prompt = f"""你是一个专业的医疗分诊助手。请根据用户的症状，进行医学推理。
        医学文献参考：{context_str}
        图谱路径：{graph_str}
        
        请严格按照以下JSON格式返回结果：
        {{
            "department": "建议就诊科室",
            "confidence": 0.92,
            "reason": "分诊理由，字数50字以内",
            "graph_nodes": [
                {{"name": "症状1", "type": "symptom"}},
                {{"name": "症状2", "type": "symptom"}},
                {{"name": "推断出的疾病1", "type": "disease"}},
                {{"name": "科室", "type": "department"}}
            ]
        }}
        注意：
        1. 你必须根据症状，主动推断出 1-2 个最可能的疾病，并将症状拆分（如头晕、恶心分开），以 "symptom" 和 "disease" 类型放入 graph_nodes。
        2. department 节点必须和上面 department 字段完全一致。
        3. 只返回JSON，绝对不要有任何其他解释文字。
        4. confidence 必须是一个0到1之间的小数。"""
    
    try:
        # 3. 调大模型生成
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": symptom}
            ],
            response_format={"type": "json_object"}
        )
        
        result_dict = json.loads(response.choices[0].message.content)
        
        # 4. 存入 SQLite 数据库
        db = SessionLocal()
        try:
            record = DiagnosisRecord(
                symptom=symptom,
                department=result_dict.get("department", "综合科"),
                confidence=result_dict.get("confidence", 0.9),
                reason=result_dict.get("reason", "")
            )
            db.add(record)
            db.commit()
        finally:
            db.close()

        # 5. 返回结果给前端
        return {
            "department": result_dict.get("department", "综合科"),
            "confidence": result_dict.get("confidence", 0.9),
            "reason": result_dict.get("reason", ""),
            "graph_nodes": result_dict.get("graph_nodes", [])
        }

    except Exception as e:
        print(f"API报错: {e}")
        return {
            "department": "系统错误",
            "confidence": 0.5,
            "reason": f"后端服务繁忙，请稍后再试。",
            "graph_nodes": [{"name": symptom, "type": "symptom"}]
        }