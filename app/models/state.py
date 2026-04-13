from typing import Annotated, Literal
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """多 Agent 协作工作流状态。

    全局字段:
    - messages: 累积的对话消息
    - session_id: 会话唯一标识
    - current_turn: 对话轮次计数器

    Agent 协作字段:
    - coordinator_plan: 协调器制定的执行计划
    - needs_copywriting: 是否需要生成文案
    - needs_image: 是否需要生成图片
    - copywriting_draft: 文案草稿内容
    - image_draft: 图片草稿 URL
    - review_feedback: 审校反馈意见
    - review_passed: 审校是否通过
    - review_cycle: 当前打回重做次数
    - max_review_cycles: 最大允许打回次数
    - final_output: 最终输出结果
    """

    messages: Annotated[list[AnyMessage], add_messages]
    session_id: str
    current_turn: int

    # 协调器
    coordinator_plan: str
    needs_copywriting: bool
    needs_image: bool

    # 专家输出
    copywriting_draft: str
    image_draft: str

    # 审校
    review_feedback: str
    review_passed: bool
    review_cycle: int
    max_review_cycles: int

    # 最终输出
    final_output: str
