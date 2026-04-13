from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langchain_core.messages import AIMessage
from app.models.state import AgentState
from app.agents import (
    coordinator_node,
    copywriter_node,
    photographer_node,
    reviewer_node,
)

MAX_REVIEW_CYCLES = 2


def route_after_coordinator(state: AgentState) -> str:
    """协调器后路由：根据计划决定下一步。"""
    if state["needs_copywriting"]:
        return "copywriter"
    elif state["needs_image"]:
        return "photographer"
    else:
        return "no_task"


def route_after_copywriter(state: AgentState) -> str:
    """文案后路由：如果还需要图片就转到摄影师，否则直接审校。"""
    if state["needs_image"]:
        return "photographer"
    else:
        return "reviewer"


def route_after_reviewer(state: AgentState) -> str:
    """审校后路由：通过则格式化输出，不通过则打回重做。"""
    if state["review_passed"]:
        return "formatter"

    # 检查是否超过最大打回次数
    if state.get("review_cycle", 0) >= MAX_REVIEW_CYCLES:
        return "formatter"  # 超过上限，强制输出

    # 打回重做
    if state["needs_copywriting"]:
        return Command(
            goto="copywriter",
            update={
                "review_feedback": state["review_feedback"],
            },
        )
    elif state["needs_image"]:
        return Command(
            goto="photographer",
            update={
                "review_feedback": state["review_feedback"],
            },
        )
    return "formatter"


def no_task_node(state: AgentState) -> AgentState:
    """空操作节点：用户请求不需要任何专家处理。"""
    return {
        "final_output": "抱歉，我无法理解您的需求。请告诉我您想生成文案还是图片？",
    }


def formatter_node(state: AgentState) -> AgentState:
    """格式化节点：汇总各 agent 的输出为最终结果。"""
    parts = []

    if state.get("coordinator_plan"):
        parts.append(f"【执行计划】{state['coordinator_plan']}")

    if state.get("copywriting_draft"):
        parts.append(f"【产品文案】\n{state['copywriting_draft']}")

    if state.get("image_draft"):
        parts.append(f"【产品图片】\n![产品图片]({state['image_draft']})")

    if state.get("review_feedback"):
        parts.append(f"【审校意见】\n{state['review_feedback']}")

    if state.get("review_cycle", 0) > 1:
        parts.append(f"（经过 {state['review_cycle']} 轮审校）")

    final = "\n\n".join(parts) if parts else "未能生成有效内容"

    return {
        "final_output": final,
        "messages": [AIMessage(content=final)],
    }


def build_workflow():
    """构建并编译多 Agent 协作工作流。"""
    graph = StateGraph(AgentState)

    # 注册 Agent 节点
    graph.add_node("coordinator", coordinator_node)
    graph.add_node("copywriter", copywriter_node)
    graph.add_node("photographer", photographer_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("no_task", no_task_node)
    graph.add_node("formatter", formatter_node)

    # 边
    graph.add_edge(START, "coordinator")

    # 协调器 → 条件路由
    graph.add_conditional_edges(
        "coordinator",
        route_after_coordinator,
        {
            "copywriter": "copywriter",
            "photographer": "photographer",
            "no_task": "no_task",
        },
    )

    # 文案 → 条件路由（可能需要图片）
    graph.add_conditional_edges(
        "copywriter",
        route_after_copywriter,
        {
            "photographer": "photographer",
            "reviewer": "reviewer",
        },
    )

    # 图片 → 审校
    graph.add_edge("photographer", "reviewer")

    # 无任务 → 结束
    graph.add_edge("no_task", END)

    # 审校 → 条件路由（打回或通过）
    graph.add_conditional_edges(
        "reviewer",
        route_after_reviewer,
        {
            "formatter": "formatter",
            "copywriter": "copywriter",
            "photographer": "photographer",
        },
    )

    # 格式化 → 结束
    graph.add_edge("formatter", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)
