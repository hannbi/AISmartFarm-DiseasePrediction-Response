from pydantic import BaseModel, Field
from typing import Optional, List


class AnalysisRequest(BaseModel):
    """실제 센서 데이터 분석 요청 모델"""
    
    crop_type: str = Field(..., description="작물 종류 (예: tomato, lettuce, cucumber)")
    equipment_list: Optional[List[str]] = Field(None, description="사용 중인 장비 목록")
    farm_location: Optional[str] = Field(None, description="스마트팜 위치")
    additional_info: Optional[str] = Field(None, description="추가 정보")
    
    class Config:
        json_schema_extra = {
            "example": {
                "crop_type": "tomato",
                "equipment_list": ["온도센서", "습도센서", "토양습도센서", "LED 조명", "환기팬"],
                "farm_location": "경기도 수원시",
                "additional_info": "방울토마토 재배 3주차"
            }
        }


class RealTimeAnalysisResponse(BaseModel):
    """실제 센서 데이터 분석 응답 모델"""
    
    # 센서 원본 데이터
    sensor_data: dict = Field(..., description="ESP32에서 받은 센서 원본 데이터")
    
    # AI 분석 결과
    analysis: dict = Field(..., description="LLM 분석 결과 (생육 환경, 질병 예측 등)")
    
    # 메타 정보
    analysis_time: str = Field(..., description="분석 수행 시각")
    request_info: dict = Field(..., description="요청 정보 (작물, 장비 등)")
