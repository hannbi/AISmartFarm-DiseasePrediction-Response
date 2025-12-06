import logging
from app.models.sensor import SensorData, ProcessedSensorData

logger = logging.getLogger(__name__)


class SensorDataPreprocessor:
    """센서 데이터 전처리 서비스"""
    
    # 작물별 최적 환경 조건 (예시)
    OPTIMAL_CONDITIONS = {
        "default": {
            "temperature": {"min": 18, "max": 28, "optimal": 23},
            "humidity": {"min": 50, "max": 70, "optimal": 60},
            "soil_moisture": {"min": 40, "max": 60, "optimal": 50}
        },
        "tomato": {
            "temperature": {"min": 20, "max": 30, "optimal": 25},
            "humidity": {"min": 50, "max": 70, "optimal": 60},
            "soil_moisture": {"min": 40, "max": 60, "optimal": 50}
        }
    }
    
    @staticmethod
    def validate_and_clean(sensor_data: SensorData) -> SensorData:
        """센서 데이터 검증 및 정제"""
        logger.info(f"Validating sensor data from device: {sensor_data.device_id}")
        
        # 데이터 유효성 검증은 Pydantic 모델에서 자동 처리
        # 추가적인 비즈니스 로직 검증
        
        return sensor_data
    
    @staticmethod
    def analyze_status(value: float, min_val: float, max_val: float) -> str:
        """값의 상태를 분석 (정상/경고/위험)"""
        if min_val <= value <= max_val:
            return "정상"
        elif min_val - 5 <= value < min_val or max_val < value <= max_val + 5:
            return "경고"
        else:
            return "위험"
    
    @classmethod
    def process(cls, sensor_data: SensorData, crop_type: str = "default") -> ProcessedSensorData:
        """센서 데이터 전처리 및 상태 분석"""
        logger.info(f"Processing sensor data for crop type: {crop_type}")
        
        # 작물 타입에 따른 최적 조건 가져오기
        conditions = cls.OPTIMAL_CONDITIONS.get(crop_type, cls.OPTIMAL_CONDITIONS["default"])
        
        # 온도 상태 분석
        temp_status = cls.analyze_status(
            sensor_data.temperature,
            conditions["temperature"]["min"],
            conditions["temperature"]["max"]
        )
        
        # 습도 상태 분석
        humidity_status = cls.analyze_status(
            sensor_data.humidity,
            conditions["humidity"]["min"],
            conditions["humidity"]["max"]
        )
        
        # 전체 상태 결정
        if temp_status == "위험" or humidity_status == "위험":
            overall_status = "위험"
        elif temp_status == "경고" or humidity_status == "경고":
            overall_status = "경고"
        else:
            overall_status = "정상"
        
        processed_data = ProcessedSensorData(
            device_id=sensor_data.device_id,
            temperature=sensor_data.temperature,
            humidity=sensor_data.humidity,
            soil_moisture=sensor_data.soil_moisture,
            light_intensity=sensor_data.light_intensity,
            co2_level=sensor_data.co2_level,
            timestamp=sensor_data.timestamp,
            temperature_status=temp_status,
            humidity_status=humidity_status,
            overall_status=overall_status
        )
        
        logger.info(f"Processed data - Overall status: {overall_status}")
        return processed_data
    
    @staticmethod
    def format_for_llm(processed_data: ProcessedSensorData) -> str:
        """LLM에 전달할 형식으로 데이터 포맷팅"""
        formatted = f"""
센서 데이터 분석 요청:
- 디바이스 ID: {processed_data.device_id}
- 측정 시각: {processed_data.timestamp}
- 온도: {processed_data.temperature}°C (상태: {processed_data.temperature_status})
- 습도: {processed_data.humidity}% (상태: {processed_data.humidity_status})
"""
        
        if processed_data.soil_moisture is not None:
            formatted += f"- 토양 습도: {processed_data.soil_moisture}%\n"
        if processed_data.light_intensity is not None:
            formatted += f"- 조도: {processed_data.light_intensity} lux\n"
        if processed_data.co2_level is not None:
            formatted += f"- CO2 농도: {processed_data.co2_level} ppm\n"
        
        formatted += f"\n전체 환경 상태: {processed_data.overall_status}"
        
        return formatted
