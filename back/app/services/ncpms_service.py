import httpx
import logging
from typing import Optional, Dict, List, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class NcpmsService:
    """국가농작물병해충관리시스템(NCPMS) API 서비스"""
    
    # 국가농작물병해충관리시스템 API 엔드포인트
    BASE_URL = "https://ncpms.rda.go.kr/npmsAPI"
    
    # 병해충 한글명 -> 영문 코드 매핑 (예시 - 실제 API 문서 참조 필요)
    DISEASE_CODE_MAP = {
        "잿빛곰팡이병": "GRAY_MOLD",
        "역병": "LATE_BLIGHT",
        "탄저병": "ANTHRACNOSE",
        "흰가루병": "POWDERY_MILDEW",
        "노균병": "DOWNY_MILDEW",
        "시들음병": "FUSARIUM_WILT",
        "잎마름병": "LEAF_BLIGHT",
        "궤양병": "CANKER",
        "점무늬병": "LEAF_SPOT",
        "모자이크병": "MOSAIC_VIRUS"
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        NCPMS API 서비스 초기화
        
        Args:
            api_key: NCPMS API 키 (환경변수에서 가져오거나 직접 전달)
        """
        self.api_key = api_key or getattr(settings, 'NCPMS_API_KEY', None)
        self.timeout = 30.0
        
    async def get_disease_info(
        self,
        disease_name: str,
        crop_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        병해충 상세 정보 조회
        
        Args:
            disease_name: 병해충 한글명
            crop_type: 작물 종류 (선택)
            
        Returns:
            병해충 정보 딕셔너리 또는 None
        """
        try:
            # 병해충 코드 매핑
            disease_code = self.DISEASE_CODE_MAP.get(disease_name)
            
            if not disease_code:
                logger.warning(f"Unknown disease name: {disease_name}")
                return None
            
            # API 호출 (실제 엔드포인트는 API 문서 확인 필요)
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "apiKey": self.api_key,
                    "diseaseCode": disease_code,
                    "cropType": crop_type or "tomato"
                }
                
                # 실제 API 엔드포인트로 교체 필요
                # response = await client.get(
                #     f"{self.BASE_URL}/disease/info",
                #     params=params
                # )
                
                # 임시: API가 없는 경우 더미 데이터 반환
                logger.info(f"Fetching disease info for: {disease_name} ({disease_code})")
                return self._get_dummy_disease_info(disease_name, disease_code)
                
        except Exception as e:
            logger.error(f"Error fetching disease info for {disease_name}: {str(e)}")
            return None
    
    async def get_disease_images(
        self,
        disease_name: str,
        limit: int = 3
    ) -> List[str]:
        """
        병해충 이미지 URL 목록 조회
        
        Args:
            disease_name: 병해충 한글명
            limit: 반환할 이미지 개수
            
        Returns:
            이미지 URL 리스트
        """
        try:
            disease_code = self.DISEASE_CODE_MAP.get(disease_name)
            
            if not disease_code:
                logger.warning(f"Unknown disease name: {disease_name}")
                return []
            
            # API 호출
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "apiKey": self.api_key,
                    "diseaseCode": disease_code,
                    "limit": limit
                }
                
                # 실제 API 엔드포인트로 교체 필요
                # response = await client.get(
                #     f"{self.BASE_URL}/disease/images",
                #     params=params
                # )
                
                # 임시: 더미 이미지 URL 반환
                logger.info(f"Fetching {limit} images for: {disease_name}")
                return self._get_dummy_images(disease_name, limit)
                
        except Exception as e:
            logger.error(f"Error fetching images for {disease_name}: {str(e)}")
            return []
    
    async def enrich_disease_info(
        self,
        disease_name: str,
        crop_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        LLM 결과를 NCPMS 데이터로 보강
        
        Args:
            disease_name: 병해충 한글명
            crop_type: 작물 종류
            
        Returns:
            보강된 병해충 정보
        """
        # 병해충 상세 정보 조회
        disease_info = await self.get_disease_info(disease_name, crop_type)
        
        # 병해충 이미지 조회
        images = await self.get_disease_images(disease_name, limit=3)
        
        if disease_info:
            disease_info["images"] = images
            return disease_info
        
        # API 조회 실패 시 기본 구조 반환
        return {
            "name": disease_name,
            "images": images,
            "description": f"{disease_name}에 대한 상세 정보를 불러올 수 없습니다.",
            "source": "NCPMS"
        }
    
    def _get_dummy_disease_info(self, disease_name: str, disease_code: str) -> Dict[str, Any]:
        """더미 병해충 정보 생성 (개발/테스트용)"""
        
        dummy_data = {
            "잿빛곰팡이병": {
                "name": "잿빛곰팡이병",
                "scientific_name": "Botrytis cinerea",
                "code": disease_code,
                "description": "잿빛곰팡이병은 고온다습한 환경에서 발생하며, 잎, 줄기, 과실에 회색 곰팡이가 발생합니다.",
                "cause": "곰팡이 (Botrytis cinerea)",
                "favorable_conditions": {
                    "temperature": "15-25°C",
                    "humidity": "85% 이상",
                    "environment": "환기 불량, 밀식 재배"
                },
                "symptoms": [
                    "잎과 줄기에 회갈색 병반 발생",
                    "습한 조건에서 회색 곰팡이 형성",
                    "과실에 수침상 병반 발생 후 곰팡이 증식",
                    "병든 부위가 말라 갈색으로 변함"
                ],
                "management": {
                    "prevention": [
                        "적정 재식 거리 유지로 통풍 개선",
                        "시설 내 환기 철저",
                        "질소질 비료 과다 시용 지양",
                        "병든 잎과 과실 조기 제거"
                    ],
                    "treatment": [
                        "등록된 살균제 살포 (펜헥사미드, 이프로디온 등)",
                        "병 발생 초기 집중 방제",
                        "약제 저항성 방지를 위한 계통 교호 살포"
                    ]
                },
                "reference_url": "https://ncpms.rda.go.kr",
                "source": "국가농작물병해충관리시스템"
            },
            "역병": {
                "name": "역병",
                "scientific_name": "Phytophthora infestans",
                "code": disease_code,
                "description": "역병은 저온다습한 환경에서 발생하며, 잎, 줄기, 과실에 급격한 병 진전을 보입니다.",
                "cause": "난균류 (Phytophthora infestans)",
                "favorable_conditions": {
                    "temperature": "18-22°C",
                    "humidity": "90% 이상",
                    "environment": "비가 자주 오는 시기, 이슬이 많은 환경"
                },
                "symptoms": [
                    "잎에 불규칙한 암갈색 병반 발생",
                    "습한 조건에서 잎 뒷면에 흰색 곰팡이",
                    "줄기에 갈색 병반, 위쪽이 시들음",
                    "과실에 갈색 병반, 빠르게 부패"
                ],
                "management": {
                    "prevention": [
                        "병든 식물체 조기 제거 및 소각",
                        "배수 관리 철저",
                        "과습 방지",
                        "저항성 품종 재배"
                    ],
                    "treatment": [
                        "등록된 살균제 예방 살포 (만코제브, 디메토모르프 등)",
                        "발병 전 예방 위주 방제",
                        "7-10일 간격 정기 살포"
                    ]
                },
                "reference_url": "https://ncpms.rda.go.kr",
                "source": "국가농작물병해충관리시스템"
            },
            "탄저병": {
                "name": "탄저병",
                "scientific_name": "Colletotrichum spp.",
                "code": disease_code,
                "description": "탄저병은 고온다습한 환경에서 발생하며, 잎과 과실에 둥근 병반이 발생합니다.",
                "cause": "곰팡이 (Colletotrichum spp.)",
                "favorable_conditions": {
                    "temperature": "25-30°C",
                    "humidity": "80% 이상",
                    "environment": "장마철, 비가 자주 오는 시기"
                },
                "symptoms": [
                    "잎에 원형의 갈색 병반",
                    "과실에 움푹 들어간 갈색 병반",
                    "병반 중앙에 분홍색 포자 덩어리",
                    "과실 부패로 이어짐"
                ],
                "management": {
                    "prevention": [
                        "통풍 및 채광 개선",
                        "빗물 튐 방지",
                        "병든 과실 조기 제거",
                        "멀칭 재배"
                    ],
                    "treatment": [
                        "등록된 살균제 살포",
                        "장마 전 예방 살포",
                        "수확 후 철저한 잔재물 제거"
                    ]
                },
                "reference_url": "https://ncpms.rda.go.kr",
                "source": "국가농작물병해충관리시스템"
            }
        }
        
        return dummy_data.get(disease_name, {
            "name": disease_name,
            "code": disease_code,
            "description": f"{disease_name}에 대한 정보",
            "source": "국가농작물병해충관리시스템"
        })
    
    def _get_dummy_images(self, disease_name: str, limit: int) -> List[str]:
        """더미 이미지 URL 생성 (개발/테스트용)"""
        
        # 실제로는 NCPMS API에서 이미지 URL을 받아옴
        # 여기서는 플레이스홀더 이미지 사용
        base_url = "https://via.placeholder.com/400x300"
        
        return [
            f"{base_url}?text={disease_name}+Example+{i+1}"
            for i in range(limit)
        ]
