from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # OpenAI 설정
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS 설정 (쉼표로 구분된 문자열을 리스트로 변환)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins를 리스트로 반환"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # RAG 설정 (OpenAI Vector Store)
    VECTOR_STORE_ID: str = ""  # vs_xxx 형식
    ASSISTANT_ID: str = ""  # asst_xxx 형식 (선택사항, 없으면 자동 생성)
    
    # 국가농작물병해충관리시스템 API 설정
    NCPMS_API_KEY: str = ""
    
    # ESP32 센서 엔드포인트
    ESP32_ENDPOINT: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
