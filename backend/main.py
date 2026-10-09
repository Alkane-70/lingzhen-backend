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
        system_prompt = f"""你是一个专业的临床辅助诊断与医学知识库系统。
        用户是医生，正在检索药物、临床指南或专业文献。
        请直接、客观地回答医生的问题，给出专业的医学解释（如药物的适应症、禁忌症、药理作用等）。
        绝对禁止出现“建议前往某科室就诊”等就医引导语。
        
        已知本地参考资料：{context_str}
        
        请严格按照以下JSON格式返回结果：
        {{
            "department": "如查询药物填'药学咨询'，如查询疾病填对应科室",
            "confidence": 0.95,
            "reason": "直接给出专业的医学解答，比如药物的功效、适应症、药理作用等，严禁使用就医建议句式，字数150字以内。",
            "graph_nodes": [
                {{"name": "查询主体（如药物名）", "type": "drug"}},
                {{"name": "相关疾病或适应症", "type": "disease"}},
                {{"name": "药理作用或相关症状", "type": "symptom"}},
                {{"name": "相关科室（如药学咨询）", "type": "department"}}
            ]
        }}
        注意：
        1. type 只能是 symptom, disease, department, drug 这四种。
        2. **图谱节点的顺序必须能构成一条完整的逻辑链！** 例如："药物" -> "主治疾病" -> "症状" -> "科室"，这样前端才能画出连线。
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
