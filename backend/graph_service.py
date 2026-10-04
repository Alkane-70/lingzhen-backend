import json
import os
import networkx as nx

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs', 'data', 'medical_data.json')

def get_graph_path(symptom):
    """构建知识图谱并查找症状对应的路径"""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return [symptom]

    # 构建有向图
    G = nx.DiGraph()
    for item in data:
        s = item.get('symptom', '')
        d = item.get('disease', '')
        dept = item.get('department', '')
        if s and d:
            G.add_edge(s, d)
        if d and dept:
            G.add_edge(d, dept)

    # 查找路径
    if symptom in G:
        # 找到直接相连的科室或疾病
        for neighbor in G.neighbors(symptom):
            for target in G.neighbors(neighbor):
                return [symptom, neighbor, target]
        # 如果只找到疾病
        for neighbor in G.neighbors(symptom):
            return [symptom, neighbor]
            
    # 如果没找到，返回简单的兜底（把输入症状和可能科室关联）
    for item in data:
        if symptom in item.get('symptom', ''):
            return [item.get('symptom'), item.get('disease'), item.get('department')]
            
    return [symptom]