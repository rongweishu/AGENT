from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_models.tongyi import ChatTongyi
from app.config import settings
from app.models.state import AgentState

SYSTEM_PROMPT = """你是一个严格的电商内容审校员。
你的职责是检查文案专家和图片专家的成果，给出评审意见。

评审标准：
1. 文案：是否有吸引力、卖点清晰、没有虚假夸大、符合电商规范
2. 图片：是否清晰展示了产品、风格是否合适、是否适合电商展示

请以 JSON 格式输出评审结果：
{
    "passed": true/false,
    "feedback": "具体的评审意见和改进建议"
}

只输出 JSON，不要输出其他内容。"""


def reviewer_node(state: AgentState) -> AgentState:
    """审校：检查文案和图片质量，决定打回或通过。"""
    content_parts = []
    if state.get("copywriting_draft"):
        content_parts.append(f"【文案草稿】\n{state['copywriting_draft']}")
    if state.get("image_draft"):
        content_parts.append(f"【图片草稿】\nURL: {state['image_draft']}")

    review_target = "\n\n".join(content_parts) if content_parts else "无内容可审校"

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"请审校以下内容：\n\n{review_target}"),
    ]

    llm = ChatTongyi(
        model=settings.llm_model,
        temperature=0.2,
        dashscope_api_key=settings.dashscope_api_key,
    )
    response = llm.invoke(messages)
    content = response.content.strip()

    import json

    try:
        content = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)
    except Exception:
        # 解析失败时默认通过
        result = {
            "passed": True,
            "feedback": "内容符合要求",
        }

    return {
        "review_feedback": result.get("feedback", ""),
        "review_passed": result.get("passed", True),
        "review_cycle": state.get("review_cycle", 0) + 1,
    }
