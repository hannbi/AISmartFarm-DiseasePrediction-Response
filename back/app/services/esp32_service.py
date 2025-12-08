import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class ESP32Service:
    """ESP32 센서 데이터 수신 서비스"""
    
    def __init__(self, esp32_endpoint: Optional[str] = None):
        """
        ESP32 서비스 초기화
        
        Args:
            esp32_endpoint: ESP32 엔드포인트 URL (환경변수 또는 직접 전달)
        """
        self.endpoint = esp32_endpoint or getattr(settings, 'ESP32_ENDPOINT', None)
        self.timeout = 10.0
        
        if not self.endpoint:
            logger.warning("ESP32_ENDPOINT not configured. Using mock data.")
    
    async def fetch_sensor_data(
        self,
        device_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        ESP32로부터 최신 센서 데이터 조회
        
        Args:
            device_id: ESP32 디바이스 ID (선택)
            
        Returns:
            센서 데이터 딕셔너리
        """
        try:
            if not self.endpoint:
                # ESP32 엔드포인트가 설정되지 않은 경우 Mock 데이터 반환
                logger.info("Using mock sensor data (ESP32 endpoint not configured)")
                return self._get_mock_sensor_data(device_id)
            
            # 실제 ESP32 API 호출
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {}
                if device_id:
                    params["device_id"] = device_id
                
                response = await client.get(
                    f"{self.endpoint}/sensor/latest",
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Fetched sensor data from ESP32: {data.get('device_id')}")
                return data
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching sensor data: {str(e)}")
            # 에러 시 Mock 데이터로 폴백
            return self._get_mock_sensor_data(device_id)
        except Exception as e:
            logger.error(f"Error fetching sensor data: {str(e)}")
            # 에러 시 Mock 데이터로 폴백
            return self._get_mock_sensor_data(device_id)
    
    def _get_mock_sensor_data(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Mock 센서 데이터 생성 (개발/테스트용)
        
        ESP32가 연결되지 않았을 때 사용
        """
        import random
        
        # 실제 센서 범위 내에서 랜덤 데이터 생성
        mock_data = {
            "device_id": device_id or "ESP32_REAL_001",
            "temperature": round(20 + random.uniform(-5, 10), 1),  # 15-30°C
            "humidity": round(50 + random.uniform(-10, 20), 1),    # 40-70%
            "soil_moisture": round(45 + random.uniform(-10, 15), 1),  # 35-60%
            "light_intensity": round(30000 + random.uniform(-10000, 20000), 1),  # 20000-50000 lux
            "co2_level": round(800 + random.uniform(-200, 400), 1),  # 600-1200 ppm
            "timestamp": datetime.now().isoformat(),
            "status": "mock",  # Mock 데이터임을 표시
            "message": "ESP32 endpoint not configured. Using mock data for development."
        }
        
        logger.info(f"Generated mock sensor data: {mock_data}")
        return mock_data
    
    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """
        ESP32 디바이스 상태 확인
        
        Args:
            device_id: ESP32 디바이스 ID
            
        Returns:
            디바이스 상태 정보
        """
        try:
            if not self.endpoint:
                return {
                    "device_id": device_id,
                    "status": "unknown",
                    "message": "ESP32 endpoint not configured"
                }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.endpoint}/device/{device_id}/status"
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error checking device status: {str(e)}")
            return {
                "device_id": device_id,
                "status": "error",
                "message": str(e)
            }
