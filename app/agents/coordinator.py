from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_models.tongyi import ChatTongyi
from app.config import settings
from app.models.state import AgentState

_llm = ChatTongyi(
    model=settings.llm_model,
    temperature=0.3,
    dashscope_api_key=settings.dashscope_api_key,
)

SYSTEM_PROMPT = """你是一个电商团队的协调员。
根据用户的需求，分析需要哪些专家来完成工作，并制定执行计划。

你的团队成员有：
1. 文案专家 - 负责撰写电商产品文案、标题、卖点描述
2. 图片专家 - 负责生成产品图片、海报

请以 JSON 格式输出你的计划，格式如下：
{
    "plan": "你的执行计划描述",
    "needs_copywriting": true/false,
    "needs_image": true/false
}

只输出 JSON，不要输出其他内容。"""


def coordinator_node(state: AgentState) -> AgentState:
    """协调器：分析用户需求，制定执行计划。"""
    user_input = state["messages"][-1].content
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"用户需求：{user_input}"),
    ]
    response = _llm.invoke(messages)
    content = response.content.strip()

    # 简单解析 JSON
    import json

    try:
        # 清理可能的 markdown 代码块
        content = content.replace("```json", "").replace("```", "").strip()
        plan = json.loads(content)
    except Exception:
        # 解析失败时默认走文案
        plan = {
            "plan": "生成产品文案",
            "needs_copywriting": True,
            "needs_image": False,
        }

    return {
        "coordinator_plan": plan.get("plan", ""),
        "needs_copywriting": plan.get("needs_copywriting", False),
        "needs_image": plan.get("needs_image", False),
        "current_turn": state["current_turn"] + 1,
    }
