import json
import os

# 找准真实数据的绝对路径
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs', 'data', 'medical_data.json')

def get_data():
    """读取真实数据"""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def search_medical_context(symptom):
    """极简版检索：查找和输入症状最匹配的医学文献"""
    data = get_data()
    results = []
    for item in data:
        text = f"症状：{item.get('symptom', '')}。可能疾病：{item.get('disease', '')}。建议科室：{item.get('department', '')}"
        # 简单的字符重合度打分
        score = sum(1 for char in symptom if char in text)
        results.append((score, text))
    
    # 降序排序，取前3个作为文献参考
    results.sort(key=lambda x: x[0], reverse=True)
    return [text for score, text in results[:3]]

def get_graph_path(symptom):
    """极简版知识图谱：返回症状->疾病->科室的路径"""
    data = get_data()
    for item in data:
        if symptom in item.get('symptom', ''):
            return [item.get('symptom'), item.get('disease'), item.get('department')]
    return [symptom]