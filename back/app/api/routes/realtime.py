from fastapi import APIRouter, HTTPException, status
from typing import Optional
import logging
from datetime import datetime

from app.models.realtime import AnalysisRequest, RealTimeAnalysisResponse
from app.models.sensor import SensorData, AIAnalysisResponse
from app.services.esp32_service import ESP32Service
from app.services.preprocessing import SensorDataPreprocessor
from app.services.ai_service import AIAnalysisService

router = APIRouter()
logger = logging.getLogger(__name__)

# 서비스 인스턴스
esp32_service = ESP32Service()
preprocessor = SensorDataPreprocessor()
ai_service = AIAnalysisService()


@router.post("/analyze-realtime", response_model=RealTimeAnalysisResponse)
async def analyze_realtime_data(request: AnalysisRequest):
    """
    실시간 센서 데이터 분석 (ESP32 연동)
    
    **실제 센서 데이터 시나리오:**
    1. 프론트엔드 → 백엔드: 분석 요청 (작물 종류, 장비 정보)
    2. 백엔드 → ESP32: 최신 센서 데이터 요청
    3. ESP32 → 백엔드: 센서 데이터 응답
    4. 백엔드: 센서 데이터 전처리
    5. 백엔드 → LLM (RAG): 분석 요청
    6. 백엔드 → NCPMS API: 병해충 이미지/정보 조회
    7. 백엔드 → 프론트엔드: **센서 원본 데이터** + LLM 분석 + NCPMS 정보
    
    **요청 데이터:**
    - crop_type: 작물 종류 (필수)
    - equipment_list: 사용 중인 장비 목록 (선택)
    - farm_location: 스마트팜 위치 (선택)
    - additional_info: 추가 정보 (선택)
    
    **응답 데이터:**
    - sensor_data: ESP32에서 받은 센서 원본 데이터
    - analysis: LLM 분석 결과 + NCPMS 병해충 정보
    - analysis_time: 분석 수행 시각
    - request_info: 요청 정보 (작물, 장비 등)
    
    Args:
        request: 분석 요청 (작물 종류, 장비 정보 등)
        
    Returns:
        RealTimeAnalysisResponse: 센서 데이터 + 분석 결과
    """
    try:
        logger.info(
            f"[REALTIME] Starting analysis - "
            f"Crop: {request.crop_type}, "
            f"Equipment: {len(request.equipment_list or [])}"
        )
        
        # 1단계: ESP32로부터 최신 센서 데이터 가져오기
        logger.info("[REALTIME] Fetching sensor data from ESP32...")
        sensor_raw_data = await esp32_service.fetch_sensor_data()
        
        # ESP32 데이터를 SensorData 모델로 변환
        sensor_data = SensorData(
            device_id=sensor_raw_data.get("device_id", "ESP32_REAL_001"),
            temperature=sensor_raw_data.get("temperature"),
            humidity=sensor_raw_data.get("humidity"),
            soil_moisture=sensor_raw_data.get("soil_moisture"),
            light_intensity=sensor_raw_data.get("light_intensity"),
            co2_level=sensor_raw_data.get("co2_level"),
            timestamp=sensor_raw_data.get("timestamp")
        )
        
        logger.info(
            f"[REALTIME] Sensor data received - "
            f"Temp: {sensor_data.temperature}°C, "
            f"Humidity: {sensor_data.humidity}%"
        )
        
        # 2단계: 센서 데이터 전처리
        validated_data = preprocessor.validate_and_clean(sensor_data)
        processed_data = preprocessor.process(validated_data, request.crop_type)
        
        logger.info(f"[REALTIME] Preprocessing completed - Status: {processed_data.overall_status}")
        
        # 3단계: LLM 입력 포맷 생성 (장비 정보 포함)
        formatted_data = preprocessor.format_for_llm(processed_data)
        
        # 사용자 컨텍스트에 장비 정보 추가
        user_context = []
        if request.equipment_list:
            user_context.append(f"사용 장비: {', '.join(request.equipment_list)}")
        if request.farm_location:
            user_context.append(f"위치: {request.farm_location}")
        if request.additional_info:
            user_context.append(f"추가 정보: {request.additional_info}")
        
        context_str = " | ".join(user_context) if user_context else None
        
        # 4단계: AI 분석 (RAG + NCPMS 통합)
        logger.info("[REALTIME] Starting AI analysis with RAG...")
        ai_response: AIAnalysisResponse = await ai_service.analyze_with_rag(
            processed_data,
            formatted_data,
            request.crop_type,
            context_str
        )
        
        logger.info(
            f"[REALTIME] Analysis completed - "
            f"Risk: {ai_response.risk_level}, "
            f"Score: {ai_response.growth_environment.overall_score:.1f}, "
            f"Diseases: {len(ai_response.diseases)}"
        )
        
        # 5단계: 응답 데이터 구성
        response = RealTimeAnalysisResponse(
            sensor_data={
                "device_id": sensor_data.device_id,
                "temperature": sensor_data.temperature,
                "humidity": sensor_data.humidity,
                "soil_moisture": sensor_data.soil_moisture,
                "light_intensity": sensor_data.light_intensity,
                "co2_level": sensor_data.co2_level,
                "timestamp": str(sensor_data.timestamp),
                "status": sensor_raw_data.get("status", "real"),
                "message": sensor_raw_data.get("message")
            },
            analysis=ai_response.dict(),
            analysis_time=datetime.now().isoformat(),
            request_info={
                "crop_type": request.crop_type,
                "equipment_list": request.equipment_list,
                "farm_location": request.farm_location,
                "additional_info": request.additional_info
            }
        )
        
        logger.info("[REALTIME] Response prepared successfully")
        return response
        
    except Exception as e:
        logger.error(f"[REALTIME] Error during analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"실시간 센서 데이터 분석 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/sensor-status")
async def get_sensor_status(device_id: Optional[str] = None):
    """
    ESP32 센서 상태 확인
    
    센서가 정상적으로 작동하는지 확인합니다.
    
    Args:
        device_id: ESP32 디바이스 ID (선택)
        
    Returns:
        센서 상태 정보
    """
    try:
        if device_id:
            status = await esp32_service.get_device_status(device_id)
        else:
            # 디바이스 ID가 없으면 최신 센서 데이터만 확인
            sensor_data = await esp32_service.fetch_sensor_data()
            status = {
                "device_id": sensor_data.get("device_id"),
                "status": sensor_data.get("status", "unknown"),
                "last_update": sensor_data.get("timestamp"),
                "message": sensor_data.get("message", "Sensor data available")
            }
        
        return status
        
    except Exception as e:
        logger.error(f"Error checking sensor status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"센서 상태 확인 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/latest-sensor-data")
async def get_latest_sensor_data():
    """
    ESP32 최신 센서 데이터 조회 (분석 없이)
    
    센서 데이터만 조회하고 싶을 때 사용합니다.
    
    Returns:
        최신 센서 데이터
    """
    try:
        sensor_data = await esp32_service.fetch_sensor_data()
        return sensor_data
        
    except Exception as e:
        logger.error(f"Error fetching latest sensor data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"센서 데이터 조회 중 오류가 발생했습니다: {str(e)}"
        )
