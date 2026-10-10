# tests/test_multiturn_dialog.py
# 灵诊智库 - 多轮追问与大病小病区分 - 后端API集成测试脚本
# 测试目标：验证 is_follow_up 字段在第三轮强制截断，以及 severity 分类是否正确

import requests
import json

url = "http://127.0.0.1:8000/api/diagnose"

# 第一轮问诊
payload1 = {
    "symptom": "头晕",
    "role": "patient",
    "history": [],
    "session_id": "test_001"
}
res1 = requests.post(url, json=payload1)
print("--- 第一轮返回 ---")
print(json.dumps(res1.json(), ensure_ascii=False, indent=2))

# 第二轮问诊（带上历史记录）
payload2 = {
    "symptom": "还伴随恶心，不想吃东西",
    "role": "patient",
    "history": [
        {"role": "user", "content": "头晕"},
        {"role": "assistant", "content": "头晕的同时是否有其他症状，比如头痛、乏力或心慌？"}
    ],
    "session_id": "test_001"
}
res2 = requests.post(url, json=payload2)
print("\n--- 第二轮返回 ---")
print(json.dumps(res2.json(), ensure_ascii=False, indent=2))

#第三轮问诊
payload3 = {
    "symptom": "有拉肚子，拉了两次了",
    "role": "patient",
    "history": [
        {"role": "user", "content": "头晕"},
        {"role": "assistant", "content": "除了头晕外，您还有其他症状吗？"},
        {"role": "user", "content": "还伴随恶心，不想吃东西"},
        {"role": "assistant", "content": "头晕、恶心、不想吃东西，是否有呕吐或腹泻的情况？"}
    ],
    "session_id": "test_001"
}
res3 = requests.post(url, json=payload3)
print("\n--- 第三轮最终结论 ---")
print(json.dumps(res3.json(), ensure_ascii=False, indent=2))