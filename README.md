# 电商内容生成 Agent

基于 FastAPI + LangGraph 多智能体架构的电商内容生成系统，结合通义千问大模型与 MCP 工具调用能力，可自动完成需求分析、文案创作、图片生成与质量审校。

## 技术栈

- **FastAPI** — REST API 服务
- **LangGraph** — 多智能体工作流编排
- **LangChain** — LLM 调用抽象
- **FastMCP** — MCP 工具协议
- **通义千问 (qwen3-max)** — 大语言模型
- **通义万相 (wanx)** — 图片生成
- **Streamlit** — Web 交互界面

## 多智能体架构

```
                    ┌─ 文案专家 ─┐
用户 → 协调器 agent ─┼─ 图片专家 ─┼→ 审校 agent → {打回重做 / 通过输出}
                    └─ 按需调用 ──┘
```

| Agent | 职责 | 自主决策 |
|-------|------|---------|
| 协调器 | 分析需求，分配任务，汇总结果 | 决定调用哪些专家 |
| 文案专家 | 生成电商文案 | 自主选风格/平台 |
| 图片专家 | 生成产品图片 | 自主选构图/色调 |
| 审校 | 检查质量，给出修改意见 | 决定打回或通过 |

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 DASHSCOPE_API_KEY
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
# 启动 FastAPI 后端
uvicorn app.main:app --host 127.0.0.1 --port 8100

# 启动 Streamlit 前端（另开一个终端）
streamlit run streamlit_app.py

# 启动 MCP Server（可选，供外部 MCP Client 调用）
python -m app.mcp_server
```

浏览器打开 **http://localhost:8501** 即可使用。

### 4. API 调用

```bash
# 生成文案
curl -X POST http://localhost:8100/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"帮我写一个保温杯的文案"}'

# 生成图片
curl -X POST http://localhost:8100/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"帮我生成一个保温杯的产品图"}'
```

API 文档: http://localhost:8100/docs

## 项目结构

```
├── app/
│   ├── agents/          # 多智能体（协调器、文案、图片、审校）
│   ├── api/             # FastAPI 路由
│   ├── graph/           # LangGraph 工作流
│   ├── models/          # 状态定义
│   ├── tools/           # MCP 工具（文案、图片生成）
│   ├── config.py        # 配置
│   ├── main.py          # FastAPI 入口
│   └── mcp_server.py    # MCP Server
├── streamlit_app.py     # Streamlit Web 界面
├── requirements.txt
└── .env.example
```
