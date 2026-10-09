import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs', 'data', 'medical_data.json')

def get_data():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def get_graph_path(symptom):
    data = get_data()
    
    # 1. 精确匹配症状
    for item in data:
        if item.get('symptom') == symptom:
            return [
                {"name": item.get('symptom'), "type": "symptom"},
                {"name": item.get('disease'), "type": "disease"},
                {"name": item.get('department'), "type": "department"}
            ]

    # 2. 字符重合度匹配
    best_match = None
    max_overlap = 0
    input_chars = set(symptom)
    for item in data:
        db_symptom = item.get('symptom', '')
        overlap = len(input_chars.intersection(set(db_symptom)))
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = item

    if best_match and max_overlap >= 2:
        return [
            {"name": best_match.get('symptom'), "type": "symptom"},
            {"name": best_match.get('disease'), "type": "disease"},
            {"name": best_match.get('department'), "type": "department"}
        ]

    # 3. 智能兜底：如果是药物查询，不再返回“疑似综合征+心血管内科”的假路径！
    # 如果识别到是药物，只返回这个药物节点，让大模型自己去构建图谱
    if any(keyword in symptom for keyword in ["丸", "片", "胶囊", "颗粒", "药", "口服液", "注射液"]):
         return [{"name": symptom, "type": "drug"}]

    # 4. 什么都不是，只返回症状节点
    return [{"name": symptom, "type": "symptom"}]
    
    # 1. 精确匹配
    for item in data:
        if item.get('symptom') == symptom:
            return [
                {"name": item.get('symptom'), "type": "symptom"},
                {"name": item.get('disease'), "type": "disease"},
                {"name": item.get('department'), "type": "department"}
            ]

    # 2. 字符重合度匹配（解决逗号分割问题）
    best_match = None
    max_overlap = 0
    input_chars = set(symptom) # 把“头晕恶心”拆成 “头,晕,恶,心”
    
    for item in data:
        db_symptom = item.get('symptom', '')
        overlap = len(input_chars.intersection(set(db_symptom))) # 看看有几个字能重合
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = item

    if best_match and max_overlap >= 2: # 只要有两个字对上了，就算匹配成功
        return [
            {"name": best_match.get('symptom'), "type": "symptom"},
            {"name": best_match.get('disease'), "type": "disease"},
            {"name": best_match.get('department'), "type": "department"}
        ]

    # 3. 终极兜底
    # 如果数据库里真没有，就给你造一个完整的数据链
    return [
        {"name": symptom, "type": "symptom"},
        {"name": "疑似综合征", "type": "disease"},
        {"name": "心血管内科", "type": "department"}
    ]
