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
from backend.database import SessionLocal, DiagnosisRecord,User

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

from typing import List, Dict

class QueryRequest(BaseModel):
    symptom: str
    role: str = "patient"
    age: str = "25岁"
    gender: str = "男"
    # 新增：用来接收前端传来的历史对话记录，初始为空列表
    history: List[Dict[str, str]] = []
    # 新增：用来区分是不是同一轮问诊
    session_id: str = "default_session"
    user_id: int = 0

class AuthRequest(BaseModel):
    username: str
    password: str


#注册接口
@app.post("/api/register")
async def register(req: AuthRequest):
    db = SessionLocal()
    try:
        # 检查用户名是否已存在
        if db.query(User).filter(User.username == req.username).first():
            return {"code": 400, "msg": "用户名已存在"}
        # 创建新用户（比赛Demo，密码暂存明文即可）
        user = User(username=req.username, password=req.password)
        db.add(user)
        db.commit()
        return {"code": 200, "msg": "注册成功", "user_id": user.id}
    finally:
        db.close()


#登录接口
@app.post("/api/login")
async def login(req: AuthRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            User.username == req.username, 
            User.password == req.password
        ).first()
        if user:
            return {"code": 200, "msg": "登录成功", "user_id": user.id, "username": user.username}
        return {"code": 400, "msg": "账号或密码错误"}
    finally:
        db.close()


#历史记录查询接口
@app.get("/api/history/{user_id}")
async def get_history(user_id: int):
    db = SessionLocal()
    try:
        # 按时间倒序查询该用户的所有记录
        records = db.query(DiagnosisRecord).filter(
            DiagnosisRecord.user_id == user_id
        ).order_by(DiagnosisRecord.id.desc()).all()
        
        return [
            {
                "id": r.id,
                "symptom": r.symptom,
                "department": r.department,
                "severity": r.severity,
                "confidence": r.confidence,
                "reason": r.reason,
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S"), # 👈 返回时间
                "chat_history": r.chat_history
            } for r in records
        ]
    finally:
        db.close()


#问诊接口
@app.post("/api/diagnose")
async def diagnose(request: QueryRequest):
    symptom = request.symptom

    # ================= 新增：提取全量历史症状 =================
    all_symptoms = symptom
    for msg in request.history:
        if msg["role"] == "user":
            all_symptoms += "、" + msg["content"]
    
    # 用全量症状去做 RAG 检索和知识图谱路径查询
    contexts = search_medical_context(all_symptoms)
    context_str = "\n".join(contexts)
    graph_nodes_local = get_graph_path(all_symptoms)
    graph_str = " -> ".join([node["name"] for node in graph_nodes_local])

    turn_count = len(request.history) // 2

    # 2. 根据角色动态生成 Prompt
    if request.role == "doctor":
        system_prompt = f"""你是一个专业的临床医药知识库系统。
        用户是医生，正在检索药物、临床指南或专业文献。
        你的任务是直接、客观地回答医生的问题，给出专业的医学解释。
        严格禁止出现“建议前往某科室就诊”、“建议您去”等任何就医引导语。
        
        已知本地参考资料：{context_str}
        
        请严格按照以下JSON格式返回结果：
        {{
            "department": "无",
            "confidence": 0.95,
            "reason": "直接给出专业的医学解答，比如药物的功效、适应症、药理作用等，严禁使用就医建议句式，字数150字以内。",
            "graph_nodes": [
                {{"name": "查询主体（如药物名）", "type": "drug"}},
                {{"name": "相关疾病或适应症", "type": "disease"}},
                {{"name": "药理作用或相关症状", "type": "symptom"}}
            ]
        }}
        注意：
        1. type 只能是 symptom(症状), disease(疾病), drug(药物) 这三种。
        2. 图谱节点的顺序必须能构成一条完整的逻辑链！
        3. 只返回JSON，绝对不要有任何其他解释文字。"""
    else:
        system_prompt = f"""你是一个专业的医疗分诊助手。当前是第 {turn_count} 轮对话。
        【绝对红线】你的输出必须是且只能是一个合法的 JSON 对象！绝对不能直接输出纯文本！
        
        医学文献参考：{context_str}
        图谱路径：{graph_str}
        
        你的任务：
        1. 判断信息是否充足。如果不足，且未超过3轮，必须进行追问。
        2. 除非用户已经连续回答了你至少 2 次追问（当前对话轮数 >= 2），否则绝对不准给出最终结论，必须继续追问。
        3. 如果信息充足，或已达到3轮，请给出最终分诊结论。
        4. 必须进行“大病小病区分”：
           如果是小病（severity: mild）：在reason中务必推荐1-2种具体的非处方药（如感冒灵颗粒、布洛芬等）和护理建议。
           如果是大病（severity: severe）：危及生命的症状（如突发剧烈胸痛、呼吸困难等），在reason中务必强烈警告“立即前往医院急诊”，绝对不准推荐自行买药。
        
        请严格按以下JSON格式返回：
        {{
            "is_follow_up": true/false,
            "follow_up_question": "如果是追问，这里写你要问的问题；否则为空字符串",
            "department": "最终结论时的建议科室",
            "severity": "mild 或 severe",
            "reason": "最终结论时的详细理由。追问阶段必须是空字符串''",
            "confidence": 0.92,
            "graph_nodes": []
        }}
        再次强调：如果你是在追问（is_follow_up 为 true），graph_nodes 必须是空数组 []，department 和 severity 必须是空字符串 ""。只返回JSON，绝对不要有任何其他文字！
        如果 is_follow_up 为 false（最终结论），graph_nodes 必须是一个完整的链路数组！必须包含：1个症状节点，1个疾病节点，1个科室节点。
        **如果 is_follow_up 为 false（最终结论），graph_nodes 的症状节点必须把历史对话中所有提到的症状都合并进去！例如历史提到了"打喷嚏"，当前提到了"流鼻涕"，图谱就必须包含"打喷嚏"和"流鼻涕"两个症状节点！** """
    
    try:
        # 1. 组装 messages
        messages = [{"role": "system", "content": system_prompt}]
        for msg in request.history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": symptom})

        # 2. 调大模型
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        # 3. 解析 JSON
        content = response.choices[0].message.content
        try:
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                result_dict = json.loads(match.group())
            else:
                result_dict = {
                    "is_follow_up": True,
                    "follow_up_question": content.strip(),
                    "department": "", "severity": "", "reason": "", "confidence": 0.5, "graph_nodes": []
                }
        except Exception as e:
            print(f"JSON解析彻底失败: {e}")
            result_dict = {
                "is_follow_up": True,
                "follow_up_question": "抱歉，系统暂时无法解析您的症状，请换一种描述方式。",
                "department": "", "severity": "", "reason": "", "confidence": 0.5, "graph_nodes": []
            }

        # ================= 第一步：强制截断追问 =================
        if turn_count >= 2:
            result_dict["is_follow_up"] = False
            if not result_dict.get("department"): result_dict["department"] = "全科门诊"
            if not result_dict.get("severity"): result_dict["severity"] = "mild"
            if not result_dict.get("reason"): result_dict["reason"] = "请注意休息，若症状加重请及时就医。"

        # ================= 第二步：重症关键词强制拦截 =================
        severe_keywords = ["胸痛", "胸闷", "呼吸困难", "大出血", "晕厥", "意识模糊", "剧烈头痛", "心梗", "脑梗", "咯血"]
        all_user_input = symptom
        for msg in request.history:
            if msg["role"] == "user":
                all_user_input += " " + msg["content"]
        
        for kw in severe_keywords:
            if kw in all_user_input:
                result_dict["severity"] = "severe"
                if not result_dict.get("department") or result_dict.get("department") == "全科门诊":
                    result_dict["department"] = "急诊科"
                if not result_dict.get("reason") or "急诊" not in result_dict.get("reason", ""):
                    result_dict["reason"] = "⚠️检测到高危重症症状，请立即拨打120或前往最近医院的【急诊科】就诊，切勿自行服药！"
                break

        # ================= 第三步：图谱强制补全 =================
        if not result_dict.get("is_follow_up", True):
            raw_nodes = result_dict.get("graph_nodes", [])
            
            # ⚠️ 新增：强制统一字段名（解决大模型偷懒用 value 而不是 name 的问题）
            for n in raw_nodes:
                if "value" in n and "name" not in n:
                    n["name"] = n.pop("value")
                elif "name" not in n:
                    n["name"] = "未知节点"
            
            # 重新提取标准化后的节点
            symptom_nodes = [n for n in raw_nodes if n.get("type") == "symptom"]
            disease_nodes = [n for n in raw_nodes if n.get("type") == "disease"]
            dept_nodes = [n for n in raw_nodes if n.get("type") == "department"]
            
            if not symptom_nodes: symptom_nodes = [{"name": all_symptoms, "type": "symptom"}] 
            if not disease_nodes: disease_nodes = [{"name": "疑似综合征", "type": "disease"}] 
            if not dept_nodes: dept_nodes = [{"name": result_dict.get("department", "综合科"), "type": "department"}]
                
            result_dict["graph_nodes"] = symptom_nodes + disease_nodes + dept_nodes
        # ==============================================================================

        # ================= 第四步：存入 SQLite =================
        is_follow_up_now = result_dict.get("is_follow_up", False)
        if not is_follow_up_now and request.user_id > 0:
            db = SessionLocal()
            try:
                record = DiagnosisRecord(
                    user_id=request.user_id,
                    symptom=all_symptoms,  # 存全量症状
                    department=result_dict.get("department", "综合科"),
                    confidence=result_dict.get("confidence", 0.9),
                    reason=result_dict.get("reason", ""),
                    session_id=request.session_id,
                    severity=result_dict.get("severity", "mild"),
                    chat_history=json.dumps(request.history, ensure_ascii=False) # 确保这里前面有个逗号
                )
                db.add(record)
                db.commit()
            finally:
                db.close()

        # 5. 返回结果
        return {
            "is_follow_up": result_dict.get("is_follow_up", False),
            "follow_up_question": result_dict.get("follow_up_question", ""),
            "department": result_dict.get("department", "综合科"),
            "severity": result_dict.get("severity", "mild"),
            "confidence": result_dict.get("confidence", 0.9),
            "reason": result_dict.get("reason", ""),
            "graph_nodes": result_dict.get("graph_nodes", [])
        }

    except Exception as e:
        print(f"API报错: {e}")
        return {
            "is_error": True,
            "is_follow_up": False,
            "department": "系统错误",
            "confidence": 0.5,
            "reason": "后端服务繁忙，请稍后再试。",
            "graph_nodes": [{"name": symptom, "type": "symptom"}]
        }
