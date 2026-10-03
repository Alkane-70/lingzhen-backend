import os
import json
from dotenv import load_dotenv, find_dotenv
from zhipuai import ZhipuAI

# 1. 自动向上寻找根目录的 .env 文件并加载
load_dotenv(find_dotenv())

# 2. 初始化智谱客户端
api_key = os.getenv("ZHIPU_API_KEY")
if not api_key:
    print("错误：没有找到 ZHIPU_API_KEY，请检查根目录的 .env 文件！")
    exit()

client = ZhipuAI(api_key=api_key)

# 3. 系统提示词（定死JSON格式）
system_prompt = """
你是一个专业的医疗分诊助手。请根据用户的症状，严格按照以下JSON格式返回结果：
{
    "department": "建议就诊科室",
    "confidence": 0.92,
    "reason": "分诊理由，字数50字以内",
    "graph_nodes": ["症状1", "症状2", "科室"]
}
注意：只返回JSON，绝对不要有任何其他解释文字。confidence 必须是一个0到1之间的小数。
"""

# 4. 模拟用户输入（正式这里会换成前端传来的数据）
user_symptom = "我最近头晕恶心，耳朵嗡嗡响"

print(f"正在调用智谱API进行分诊... 用户症状: {user_symptom}\n")

try:
    # 5. 发起请求
    response = client.chat.completions.create(
        model="glm-4-flash", # 使用 glm-4-flash 模型
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_symptom}
        ],
        response_format={"type": "json_object"} # 强制开启JSON模式
    )

    # 6. 解析并打印结果
    result_json = response.choices[0].message.content
    result_dict = json.loads(result_json)
    
    print("API 调用成功！返回的标准 JSON 如下：")
    print(json.dumps(result_dict, ensure_ascii=False, indent=2))
    print("\n--- Day 1 后端验收通过！---")

except Exception as e:
    print(f" 运行报错: {e}")
    print("排查建议：检查 .env 里的密钥是否正确，或者网络是否通畅。")