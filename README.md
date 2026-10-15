# 灵诊智库 (LingZhen_Project)

## 📌 项目简介
灵诊智库是一个基于大模型、RAG（检索增强生成）与知识图谱的智能辅助分诊系统。
本项目专为 AIC 大赛智能软件创新赛道开发，采用 **Local-First（本地优先）架构**，旨在解决大众“大病小病分不清”以及通用大模型在医疗领域容易产生“幻觉”的痛点。
系统支持最多三轮拟人化追问、大病小病智能分级（轻症建议OTC药物，重症急诊预警），并通过 ECharts 动态呈现“症状-疾病-科室”的知识图谱推理过程。

## 🛠 技术栈
- **前端**：Vue 3 + Vite + Element Plus + ECharts（知识图谱可视化）
- **后端**：Python 3.10 + FastAPI + SQLAlchemy + SQLite（本地数据持久化）
- **AI 核心**：智谱 GLM-4-Flash API + NetworkX（知识图谱构建）+ 轻量级 RAG 检索
- **工程规范**：Git 版本控制、接口测试脚本（tests/）

## 👥 团队分工
- **成员1（队长）**：后端开发与AI算法。负责RAG流水线、知识图谱构建、Prompt工程、重症强制拦截、数据库接入及接口测试。
- **成员2**：前端开发与可视化。负责Vue3页面搭建、账号与历史档案UI、Axios接口联调、ECharts动态图谱渲染及交互优化。
- **成员3**：数据与工程文档。负责医疗数据集清洗、数据库表结构设计、系统测试用例编写，以及全套参赛材料（技术方案、PPT、演示视频）的策划与制作。

## 💻 系统启动步骤

### 1. 环境准备
- 确保电脑已安装 Python 3.10+ 和 Node.js (v18+)。
- 注册智谱AI开放平台账号，获取 `ZHIPU_API_KEY`。

### 2. 配置环境变量（极其重要！）
在项目**根目录**新建一个 `.env` 文件（不要提交到Git），填入你的API Key：
```env
ZHIPU_API_KEY=你的智谱API_KEY
```

### 3. 启动后端 (FastAPI)
打开终端，在项目根目录下执行：

```env
# 创建并激活虚拟环境
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 启动后端服务
python -m uvicorn backend.main:app --reload
```

后端启动成功后，可访问 http://127.0.0.1:8000/docs 查看接口文档。

### 4. 启动前端 (Vue3)
新开一个终端，进入前端目录并启动：

```env
cd frontend/web
npm install
npm run dev
```

前端启动成功后，浏览器访问终端提示的地址（通常是 http://localhost:5173）即可使用系统。

## 📁 目录结构说明
backend/：后端核心代码（main.py 接口、rag_service.py RAG检索、graph_service.py 图谱构建、database.py 数据库）。

frontend/web/：前端Vue3工程代码。

docs/：技术方案、医疗数据集、测试用例及建表语句。

backend/tests/：多轮对话与账号系统的集成测试脚本。

## ⚠️ 免责声明
本系统仅为健康科普辅助分诊工具，不替代执业医师诊断。最终诊断请遵医嘱。