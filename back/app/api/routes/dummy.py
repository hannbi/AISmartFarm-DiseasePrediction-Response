from fastapi import APIRouter, HTTPException, status
from typing import Optional, List
from pydantic import BaseModel
import logging

from app.models.sensor import SensorData, AIAnalysisResponse
from app.services.preprocessing import SensorDataPreprocessor
from app.services.ai_service import AIAnalysisService

router = APIRouter()
logger = logging.getLogger(__name__)


class DummyAnalysisRequest(BaseModel):
    """더미 데이터 분석 요청 모델"""
    sensor_data: SensorData
    crop_type: Optional[str] = "tomato"
    equipment_list: Optional[List[str]] = None
    user_context: Optional[str] = None

# 서비스 인스턴스
preprocessor = SensorDataPreprocessor()
ai_service = AIAnalysisService()


@router.post("/analyze-dummy", response_model=AIAnalysisResponse)
async def analyze_dummy_data(request: DummyAnalysisRequest):
    """
    더미 센서 데이터 분석 (프론트엔드 테스트용)
    
    **시나리오:**
    1. 프론트엔드에서 더미 센서 데이터 전송
    2. 백엔드에서 전처리 수행
    3. LLM (RAG) 분석 요청
    4. LLM 결과 + NCPMS 병해충 정보 통합
    5. 프론트엔드로 통합 결과 반환
    
    **응답에 포함되는 정보:**
    - 생육 환경 점수 및 평가
    - 질병 발생 확률 예측 (확률 순 정렬)
    - 병해충 이미지 (NCPMS API)
    - 병해충 상세 정보 (학명, 증상, 방제법 등)
    - 맞춤형 권장 조치
    
    Args:
        sensor_data: 더미 센서 데이터
        crop_type: 작물 종류 (default: tomato)
        user_context: 사용자 추가 정보
        
    Returns:
        AIAnalysisResponse: LLM 분석 + NCPMS 병해충 정보 통합 결과
    """
    try:
        logger.info(f"[DUMMY] Starting analysis for device: {request.sensor_data.device_id}, crop: {request.crop_type}")
        
        # 1단계: 데이터 전처리
        validated_data = preprocessor.validate_and_clean(request.sensor_data)
        processed_data = preprocessor.process(validated_data, request.crop_type)
        
        logger.info(f"[DUMMY] Preprocessing completed - Status: {processed_data.overall_status}")
        
        # 2단계: LLM 입력 포맷 생성
        formatted_data = preprocessor.format_for_llm(processed_data)
        
        # 사용자 컨텍스트에 장비 정보 추가
        user_context_text = request.user_context or ""
        if request.equipment_list:
            equipment_info = f"사용 장비: {', '.join(request.equipment_list)}"
            user_context_text = f"{user_context_text}\n{equipment_info}" if user_context_text else equipment_info
        
        # 3단계: AI 분석 (RAG 활용)
        # - LLM이 생육 환경 점수 및 질병 예측 수행
        # - 예측된 질병명을 기반으로 NCPMS API 호출
        # - 병해충 이미지 및 상세 정보 통합
        ai_response = await ai_service.analyze_with_rag(
            processed_data,
            formatted_data,
            request.crop_type,
            user_context_text
        )
        
        logger.info(
            f"[DUMMY] Analysis completed - "
            f"Risk: {ai_response.risk_level}, "
            f"Diseases detected: {len(ai_response.diseases)}"
        )
        
        # 병해충 정보 로깅
        for disease in ai_response.diseases:
            logger.info(
                f"[DUMMY] Disease: {disease.name} "
                f"({disease.probability:.1f}%), "
                f"Images: {len(disease.images or [])}"
            )
        
        return ai_response
        
    except Exception as e:
        logger.error(f"[DUMMY] Error during analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"더미 데이터 분석 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/test-ncpms/{disease_name}")
async def test_ncpms_api(disease_name: str):
    """
    NCPMS API 테스트 엔드포인트
    
    병해충명을 입력하면 NCPMS에서 이미지와 상세 정보를 조회합니다.
    
    Args:
        disease_name: 병해충 한글명 (예: 잿빛곰팡이병, 역병, 탄저병)
        
    Returns:
        NCPMS 병해충 정보
    """
    try:
        from app.services.ncpms_service import NcpmsService
        
        ncpms = NcpmsService()
        result = await ncpms.enrich_disease_info(disease_name)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"병해충 정보를 찾을 수 없습니다: {disease_name}"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"NCPMS API test error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NCPMS API 테스트 중 오류가 발생했습니다: {str(e)}"
        )
