from fastapi import APIRouter, HTTPException, status
from typing import Optional
import logging

from app.models.sensor import (
    SensorData,
    ProcessedSensorData,
    AIAnalysisRequest,
    AIAnalysisResponse
)
from app.services.preprocessing import SensorDataPreprocessor
from app.services.ai_service import AIAnalysisService

router = APIRouter()
logger = logging.getLogger(__name__)

# 서비스 인스턴스
preprocessor = SensorDataPreprocessor()
ai_service = AIAnalysisService()


@router.post("/data", response_model=ProcessedSensorData)
async def receive_sensor_data(
    sensor_data: SensorData,
    crop_type: Optional[str] = "default"
):
    """
    ESP32로부터 센서 데이터 수신 및 전처리
    
    - **device_id**: ESP32 디바이스 ID
    - **temperature**: 온도 (°C)
    - **humidity**: 습도 (%)
    - **soil_moisture**: 토양 습도 (%) - 선택
    - **light_intensity**: 조도 (lux) - 선택
    - **co2_level**: CO2 농도 (ppm) - 선택
    """
    try:
        logger.info(f"Received sensor data from device: {sensor_data.device_id}")
        
        # 데이터 검증 및 정제
        validated_data = preprocessor.validate_and_clean(sensor_data)
        
        # 데이터 전처리 및 상태 분석
        processed_data = preprocessor.process(validated_data, crop_type)
        
        return processed_data
        
    except Exception as e:
        logger.error(f"Error processing sensor data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"센서 데이터 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_sensor_data(
    sensor_data: SensorData,
    crop_type: Optional[str] = "default",
    user_context: Optional[str] = None
):
    """
    센서 데이터 수신 → 전처리 → AI 분석 (통합 엔드포인트)
    
    ESP32에서 데이터를 받아 전처리하고 GPT RAG를 통해 병해 예측 및 권장사항 제공
    """
    try:
        logger.info(f"Starting full analysis for device: {sensor_data.device_id}")
        
        # 1단계: 데이터 전처리
        validated_data = preprocessor.validate_and_clean(sensor_data)
        processed_data = preprocessor.process(validated_data, crop_type)
        
        # 2단계: LLM 입력 포맷 생성
        formatted_data = preprocessor.format_for_llm(processed_data)
        
        # 3단계: AI 분석 (RAG 활용)
        ai_response = await ai_service.analyze_with_rag(
            processed_data,
            formatted_data,
            crop_type,
            user_context
        )
        
        logger.info(f"Analysis completed - Risk level: {ai_response.risk_level}")
        return ai_response
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"분석 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/analyze-processed", response_model=AIAnalysisResponse)
async def analyze_processed_data(request: AIAnalysisRequest):
    """
    이미 전처리된 데이터에 대한 AI 분석
    
    전처리가 완료된 데이터를 받아 AI 분석만 수행
    """
    try:
        logger.info(f"Analyzing processed data for device: {request.sensor_data.device_id}")
        
        # LLM 입력 포맷 생성
        formatted_data = preprocessor.format_for_llm(request.sensor_data)
        
        # AI 분석
        ai_response = await ai_service.analyze_with_rag(
            request.sensor_data,
            formatted_data,
            request.crop_type,
            request.user_context
        )
        
        return ai_response
        
    except Exception as e:
        logger.error(f"Error during processed data analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"분석 중 오류가 발생했습니다: {str(e)}"
        )
