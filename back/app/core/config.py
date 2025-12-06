from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # OpenAI 설정
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS 설정
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # RAG 설정
    RAG_ENDPOINT: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
