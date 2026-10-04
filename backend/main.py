from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from zhipuai import ZhipuAI
import json
import os
from dotenv import load_dotenv, find_dotenv
from backend.rag_service import search_medical_context
from backend.graph_service import get_graph_path

load_dotenv(find_dotenv())
client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))

app = FastAPI(title="灵诊智库后端")

# 允许跨域请求，保证前端能调通
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SymptomRequest(BaseModel):
    symptom: str

@app.post("/api/diagnose")
async def diagnose(req: SymptomRequest):
    symptom = req.symptom
    
    # 1. RAG 检索文献
    contexts = search_medical_context(symptom)
    context_str = "\n".join(contexts)
    
    # 2. 知识图谱查路径
    graph_nodes = get_graph_path(symptom)
    graph_str = " -> ".join([str(node) for node in graph_nodes])
    
    # 3. 拼装 Prompt
    system_prompt = f"""你是一个专业的医疗分诊助手。请根据用户症状，结合以下资料，返回标准JSON。
    医学文献参考：{context_str}
    图谱路径：{graph_str}
    
    请严格按以下JSON格式返回：
    {{
        "department": "建议科室",
        "confidence": 0.92,
        "reason": "分诊理由",
        "graph_nodes": ["症状1", "症状2", "科室"]
    }}
    注意：只返回JSON，不能有其他文字。confidence 必须在0到1之间。"""

    # 4. 调大模型生成
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": symptom}
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)