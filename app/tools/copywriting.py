from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings

_copywriting_llm = ChatTongyi(
    model=settings.llm_model,
    temperature=settings.default_temperature,
    dashscope_api_key=settings.dashscope_api_key,
)

SYSTEM_PROMPT = """你是一个专业的电商文案生成助手。
根据用户提供的产品信息、风格和平台，生成高质量、有吸引力的电商文案。
要求：
1. 标题要吸引眼球，突出产品卖点
2. 描述要清晰、生动、有说服力
3. 根据不同平台风格调整语气（如小红书偏种草、淘宝偏促销、抖音偏短视频风格）
4. 适当使用emoji增强表现力
5. 输出格式清晰，分标题、卖点描述、行动号召等部分"""


def generate_copywriting_tool(product_info: str, style: str = "专业", platform: str = "通用") -> str:
    """生成电商产品文案。

    Args:
        product_info: 产品信息（名称、特点、目标受众等）
        style: 文案风格（专业、活泼、文艺、幽默等）
        platform: 目标平台（淘宝、小红书、抖音、京东、通用）

    Returns:
        生成的文案文本
    """
    user_prompt = f"""
产品信息：{product_info}
文案风格：{style}
发布平台：{platform}

请为该产品生成完整的电商文案。"""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]
    response = _copywriting_llm.invoke(messages)
    return response.content
