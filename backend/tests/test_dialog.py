import requests
import json

# 确保你的后端正在运行：python -m uvicorn backend.main:app --reload
url = "http://127.0.0.1:8000/api/diagnose"
session_id = "test_session_001"

def send_request(payload, title):
    print(f"\n{'='*20} {title} {'='*20}")
    try:
        res = requests.post(url, json=payload, timeout=30)
        print(f"HTTP状态码: {res.status_code}")
        print(json.dumps(res.json(), ensure_ascii=False, indent=2))
        return res.json()
    except Exception as e:
        print(f"请求失败: {e}")
        return {}

# ==================== 测试场景1：普通多轮追问（小病） ====================
print("\n\n==== 测试场景1：普通多轮追问（小病） ====")

# 第一轮
payload1 = {
    "symptom": "打喷嚏",
    "role": "patient",
    "history": [],
    "session_id": session_id,
    "user_id": 1
}
res1 = send_request(payload1, "第1轮：打喷嚏")

# 第二轮（带上第一轮的历史）
history2 = [
    {"role": "user", "content": "打喷嚏"},
    {"role": "assistant", "content": res1.get("follow_up_question", "除了打喷嚏，还有其他症状吗？")}
]
payload2 = {
    "symptom": "流鼻涕",
    "role": "patient",
    "history": history2,
    "session_id": session_id,
    "user_id": 1
}
res2 = send_request(payload2, "第2轮：流鼻涕")

# 第三轮（强制出结论）
history3 = history2 + [
    {"role": "user", "content": "流鼻涕"},
    {"role": "assistant", "content": res2.get("follow_up_question", "是否伴有发热？")}
]
payload3 = {
    "symptom": "不发热",
    "role": "patient",
    "history": history3,
    "session_id": session_id,
    "user_id": 1
}
res3 = send_request(payload3, "第3轮：不发热（应该出最终结论）")

# 验证小病图谱是否包含所有历史症状
print("\n【小病测试结论验证】")
if res3.get("severity") == "mild":
    print("✅ 小病判断正确 (mild)")
else:
    print(f"❌ 小病判断错误，当前为: {res3.get('severity')}")

symptoms_in_graph = [node.get("name", node.get("value", "未知")) for node in res3.get("graph_nodes", []) if node.get("type") == "symptom"]
print(f"图谱中的症状节点: {symptoms_in_graph}")
if "打喷嚏" in symptoms_in_graph and "流鼻涕" in symptoms_in_graph:
    print("✅ 历史症状合并成功！")
else:
    print("❌ 历史症状合并失败，图谱只显示了部分症状。")


# ==================== 测试场景2：重症强制拦截（大病） ====================
print("\n\n==== 测试场景2：重症强制拦截（大病） ====")

# 模拟直接问胸痛（三轮对话）
h1 = [{"role": "user", "content": "胸口痛"}]
p1 = {"symptom": "胸口痛", "role": "patient", "history": [], "session_id": "test_002", "user_id": 1}
r1 = send_request(p1, "大病第1轮：胸口痛")

h2 = h1 + [{"role": "assistant", "content": r1.get("follow_up_question", "是否呼吸困难？")}]
p2 = {"symptom": "有呼吸困难", "role": "patient", "history": h2, "session_id": "test_002", "user_id": 1}
r2 = send_request(p2, "大病第2轮：呼吸困难")

h3 = h2 + [{"role": "user", "content": "有呼吸困难"}, {"role": "assistant", "content": r2.get("follow_up_question", "还有其他症状吗？")}]
p3 = {"symptom": "还出汗", "role": "patient", "history": h3, "session_id": "test_002", "user_id": 1}
r3 = send_request(p3, "大病第3轮：还出汗（应该触发重症拦截）")

print("\n【大病测试结论验证】")
if r3.get("severity") == "severe":
    print("✅ 重症强制拦截成功！(severe)")
else:
    print(f"❌ 重症拦截失败，当前为: {r3.get('severity')}")

if r3.get("department") == "急诊科":
    print("✅ 科室强制修改为急诊科成功！")
else:
    print(f"❌ 科室未修改为急诊科，当前为: {r3.get('department')}")

if "急诊" in r3.get("reason", ""):
    print("✅ 理由中成功包含急诊警告！")
else:
    print("❌ 理由中未包含急诊警告。")