import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass(frozen=True)
class Settings:
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "qwen-max")
    image_model: str = os.getenv("IMAGE_MODEL", "wanx2.1-t2i-turbo")
    image_size: str = os.getenv("IMAGE_SIZE", "1024*1024")
    default_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    max_conversation_history: int = 20  # max messages to keep in context


settings = Settings()
