from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_models.tongyi import ChatTongyi
from app.config import settings
from app.models.state import AgentState
from app.mcp_server import mcp as mcp_server

_prompt_llm = ChatTongyi(
    model=settings.llm_model,
    temperature=0.7,
    dashscope_api_key=settings.dashscope_api_key,
)

PHOTOGRAPHER_SYSTEM = """你是一个资深商业摄影总监。
根据产品描述，你自主决定拍摄风格、构图、色调、场景布置，
然后生成高质量的产品图片。

你需要先规划拍摄方案，再调用图片生成工具执行。"""


async def photographer_node(state: AgentState) -> AgentState:
    """图片专家：自主决定构图/色调，调用万相生成图片。"""
    user_input = state["messages"][-1].content

    # 先用 LLM 规划拍摄方案
    plan_messages = [
        SystemMessage(
            content="你是一个商业摄影总监。请用一句话描述这个产品应该用什么风格拍摄，包括构图、色调、场景等。只输出一句话描述，不要输出其他。"
        ),
        HumanMessage(content=f"产品：{user_input}"),
    ]
    plan_response = _prompt_llm.invoke(plan_messages)
    style_description = plan_response.content.strip()

    # 调用 MCP 工具生成图片
    tool = await mcp_server.get_tool("generate_image")
    image_url = tool.fn(
        product_description=f"{user_input}。{style_description}",
        style="电商摄影",
    )

    return {
        "image_draft": image_url,
    }
