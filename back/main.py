from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api.routes import sensor, health

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 이벤트"""
    logger.info("Starting AI Smart Farm Backend Server...")
    yield
    logger.info("Shutting down AI Smart Farm Backend Server...")


# FastAPI 앱 초기화
app = FastAPI(
    title="AI Smart Farm API",
    description="ESP32 센서 데이터 수신 및 RAG 기반 병해 예측 시스템",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(sensor.router, prefix="/api/sensor", tags=["Sensor"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Smart Farm Backend API",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
