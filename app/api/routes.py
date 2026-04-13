from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.graph.workflow import build_workflow
import uuid

router = APIRouter(prefix="/api/v1", tags=["agent"])

workflow = build_workflow()


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    plan: str
    review_passed: bool
    review_cycle: int


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    initial_state = {
        "messages": [{"role": "user", "content": request.message}],
        "session_id": session_id,
        "current_turn": 0,
        "coordinator_plan": "",
        "needs_copywriting": False,
        "needs_image": False,
        "copywriting_draft": "",
        "image_draft": "",
        "review_feedback": "",
        "review_passed": False,
        "review_cycle": 0,
        "max_review_cycles": 2,
        "final_output": "",
    }

    try:
        result = await workflow.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": session_id}},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(
        reply=result["final_output"],
        session_id=session_id,
        plan=result["coordinator_plan"],
        review_passed=result["review_passed"],
        review_cycle=result["review_cycle"],
    )
