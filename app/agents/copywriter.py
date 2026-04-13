from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_models.tongyi import ChatTongyi
from app.config import settings
from app.models.state import AgentState

_llm = ChatTongyi(
    model=settings.llm_model,
    temperature=settings.default_temperature,
    dashscope_api_key=settings.dashscope_api_key,
)

SYSTEM_PROMPT = """你是一个资深电商文案专家。
你自主决定文案的风格和平台策略，根据产品信息输出高质量的电商文案。

要求：
1. 标题吸引眼球，突出核心卖点
2. 描述清晰生动，有说服力
3. 根据产品类型自动调整语气和风格
4. 适当使用 emoji 增强表现力
5. 输出格式：标题、卖点、详细描述、行动号召"""


def copywriter_node(state: AgentState) -> AgentState:
    """文案专家：自主决策生成电商文案。"""
    user_input = state["messages"][-1].content

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=f"产品信息：{user_input}\n\n请根据你的专业判断，选择最合适的风格和平台，生成完整的电商文案。"
        ),
    ]
    response = _llm.invoke(messages)

    return {
        "copywriting_draft": response.content,
    }
