from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SensorData(BaseModel):
    """ESP32로부터 받는 센서 데이터 모델"""
    
    device_id: str = Field(..., description="ESP32 디바이스 ID")
    temperature: float = Field(..., description="온도 (°C)", ge=-50, le=100)
    humidity: float = Field(..., description="습도 (%)", ge=0, le=100)
    soil_moisture: Optional[float] = Field(None, description="토양 습도 (%)", ge=0, le=100)
    light_intensity: Optional[float] = Field(None, description="조도 (lux)", ge=0)
    co2_level: Optional[float] = Field(None, description="CO2 농도 (ppm)", ge=0)
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="데이터 수집 시각")
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "ESP32_001",
                "temperature": 25.5,
                "humidity": 65.0,
                "soil_moisture": 45.0,
                "light_intensity": 5000.0,
                "co2_level": 800.0,
                "timestamp": "2025-12-06T10:30:00"
            }
        }


class ProcessedSensorData(BaseModel):
    """전처리된 센서 데이터"""
    
    device_id: str
    temperature: float
    humidity: float
    soil_moisture: Optional[float] = None
    light_intensity: Optional[float] = None
    co2_level: Optional[float] = None
    timestamp: datetime
    
    # 추가 분석 정보
    temperature_status: str = Field(..., description="온도 상태 (정상/경고/위험)")
    humidity_status: str = Field(..., description="습도 상태 (정상/경고/위험)")
    overall_status: str = Field(..., description="전체 환경 상태")
    

class AIAnalysisRequest(BaseModel):
    """AI 분석 요청 모델"""
    
    sensor_data: ProcessedSensorData
    crop_type: Optional[str] = Field(None, description="작물 종류")
    user_context: Optional[str] = Field(None, description="사용자 추가 정보")


class DiseaseInfo(BaseModel):
    """질병 정보 모델"""
    
    name: str = Field(..., description="질병명")
    probability: float = Field(..., description="발생 확률 (%)", ge=0, le=100)
    reason: str = Field(..., description="발생 원인/조건")
    symptoms: Optional[str] = Field(None, description="주요 증상")
    prevention: Optional[str] = Field(None, description="예방 방법")
    
    # NCPMS 연동 추가 필드
    scientific_name: Optional[str] = Field(None, description="학명")
    images: Optional[list[str]] = Field(None, description="병해충 이미지 URL 목록")
    detailed_symptoms: Optional[list[str]] = Field(None, description="상세 증상 목록")
    management: Optional[dict] = Field(None, description="방제 정보 (예방, 치료)")
    reference_url: Optional[str] = Field(None, description="참고 URL")
    source: Optional[str] = Field(None, description="정보 출처")


class GrowthEnvironmentScore(BaseModel):
    """생육 환경 평가 모델"""
    
    overall_score: float = Field(..., description="전체 생육 환경 점수 (0-100)", ge=0, le=100)
    status: str = Field(..., description="생육 환경 상태 (최적/양호/주의/불량)")
    temperature_score: float = Field(..., description="온도 적합도 점수", ge=0, le=100)
    humidity_score: float = Field(..., description="습도 적합도 점수", ge=0, le=100)
    soil_moisture_score: Optional[float] = Field(None, description="토양 습도 적합도 점수", ge=0, le=100)
    detail: str = Field(..., description="상세 평가 내용")


class AIAnalysisResponse(BaseModel):
    """AI 분석 응답 모델"""
    
    # 생육 환경 평가
    growth_environment: GrowthEnvironmentScore = Field(..., description="생육 환경 평가 결과")
    
    # 질병 예측
    diseases: list[DiseaseInfo] = Field(..., description="질병 발생 확률 목록 (확률 순 정렬)")
    risk_level: str = Field(..., description="전체 위험도 (낮음/중간/높음)")
    
    # 권장 조치
    recommendations: list[str] = Field(..., description="권장 조치 사항")
    optimal_conditions: dict = Field(..., description="최적 환경 조건")
    
    # 메타 정보
    analysis_summary: str = Field(..., description="종합 분석 요약")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "growth_environment": {
                    "overall_score": 75.5,
                    "status": "양호",
                    "temperature_score": 85.0,
                    "humidity_score": 60.0,
                    "soil_moisture_score": 80.0,
                    "detail": "현재 온도는 최적 범위이나, 습도가 다소 높은 상태입니다."
                },
                "diseases": [
                    {
                        "name": "잿빛곰팡이병",
                        "probability": 68.5,
                        "reason": "습도 70% 이상 유지, 환기 부족",
                        "symptoms": "잎과 줄기에 회색 곰팡이 발생",
                        "prevention": "습도 관리 및 환기 강화"
                    },
                    {
                        "name": "역병",
                        "probability": 42.0,
                        "reason": "토양 과습, 고온다습 환경",
                        "symptoms": "잎이 시들고 갈색으로 변함",
                        "prevention": "배수 관리 및 과습 방지"
                    }
                ],
                "risk_level": "중간",
                "recommendations": [
                    "환기를 통해 습도를 60% 이하로 낮추세요",
                    "물 주기를 줄이고 토양 배수를 확인하세요",
                    "예방적 살균제 살포를 고려하세요"
                ],
                "optimal_conditions": {
                    "temperature": "20-25°C",
                    "humidity": "50-60%",
                    "soil_moisture": "40-50%"
                },
                "analysis_summary": "토마토 생육 환경은 전반적으로 양호하나, 높은 습도로 인해 곰팡이성 질병 발생 위험이 있습니다.",
                "timestamp": "2025-12-06T10:30:00"
            }
        }
