import requests
import json
import time

# 后端基础地址
BASE_URL = "http://127.0.0.1:8000"

def print_res(title, data):
    print(f"\n--- {title} ---")
    print(json.dumps(data, ensure_ascii=False, indent=2))

# 1. 生成一个随机用户名，防止重复注册报错
timestamp = str(int(time.time()))
username = f"test_user_{timestamp}"
password = "123456"

print(f"本次测试账号: {username} / {password}")

# ==================== 测试1：注册新账号 ====================
reg_payload = {"username": username, "password": password}
res_reg = requests.post(f"{BASE_URL}/api/register", json=reg_payload).json()
print_res("1. 注册结果", res_reg)

if res_reg.get("code") != 200:
    print("注册失败，终止测试。请检查后端是否启动，或数据库是否已更新。")
    exit()

# ==================== 测试2：登录并获取 user_id ====================
login_payload = {"username": username, "password": password}
res_login = requests.post(f"{BASE_URL}/api/login", json=login_payload).json()
print_res("2. 登录结果", res_login)

user_id = res_login.get("user_id")
if not user_id:
    print("登录失败，未获取到 user_id。")
    exit()
print(f"获取到的 user_id: {user_id}")

# ==================== 测试3：携带 user_id 进行问诊 ====================
diagnose_payload = {
    "symptom": "头晕恶心",
    "role": "patient",
    "history": [],
    "session_id": f"session_{timestamp}",
    "user_id": user_id  # 👈 关键：把刚刚登录获取的 user_id 传进去
}
res_diagnose = requests.post(f"{BASE_URL}/api/diagnose", json=diagnose_payload).json()
print_res("3. 问诊结果", res_diagnose)

# ==================== 测试4：查询该用户的历史记录 ====================
res_history = requests.get(f"{BASE_URL}/api/history/{user_id}").json()
print_res("4. 历史记录查询结果", res_history)

# 校验历史记录是否成功存入
if len(res_history) > 0 and res_history[0].get("symptom") == "头晕恶心":
    print("\n✅ 测试全部通过！历史记录与账号绑定成功！")
else:
    print("\n❌ 测试失败：未能在历史记录中找到刚才的问诊数据。")