from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="E-commerce Agent API",
    description="电商文案与图片生成 Agent，基于 Qwen-Max + 通义万相",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
async def root():
    return {"message": "E-commerce Agent API is running"}
