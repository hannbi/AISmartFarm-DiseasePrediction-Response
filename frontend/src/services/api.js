/**
 * AI Smart Farm Backend API Service
 * 
 * 백엔드 API와의 통신을 담당하는 서비스 레이어
 */

import axios from 'axios';

// API Base URL (환경변수에서 가져오기)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 120000; // 2분

// Axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 (로깅)
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터 (에러 핸들링)
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.config.url} - ${response.status}`);
    return response;
  },
  (error) => {
    console.error('[API Response Error]', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * API Service 객체
 */
const api = {
  /**
   * 헬스체크
   */
  healthCheck: async () => {
    const response = await apiClient.get('/api/health');
    return response.data;
  },

  /**
   * 센서 데이터 전처리
   * @param {Object} sensorData - 센서 데이터
   * @param {string} cropType - 작물 종류 (tomato, lettuce, etc.)
   */
  preprocessSensorData: async (sensorData, cropType = 'tomato') => {
    const response = await apiClient.post('/api/sensor/data', sensorData, {
      params: { crop_type: cropType }
    });
    return response.data;
  },

  /**
   * 더미 데이터 분석 (프론트엔드 테스트용)
   * @param {Object} payload - 분석 요청 데이터
   * @param {Object} payload.sensor_data - 센서 데이터
   * @param {string} payload.crop_type - 작물 종류
   * @param {Array<string>} payload.equipment_list - 장비 목록
   * @param {string} payload.user_context - 사용자 추가 정보
   */
  analyzeDummyData: async (payload) => {
    const response = await apiClient.post('/api/dummy/analyze-dummy', payload);
    return response.data;
  },

  /**
   * 실시간 센서 분석 (프로덕션용 - ESP32 연동)
   * @param {Object} payload - 분석 요청 데이터
   * @param {string} payload.crop_type - 작물 종류
   * @param {Array<string>} payload.equipment_list - 장비 목록
   * @param {string} payload.farm_location - 농장 위치
   * @param {string} payload.additional_info - 추가 정보
   */
  analyzeRealtimeData: async (payload) => {
    const response = await apiClient.post('/api/realtime/analyze-realtime', payload);
    return response.data;
  },

  /**
   * ESP32 센서 상태 확인
   * @param {string} deviceId - 디바이스 ID (선택)
   */
  getSensorStatus: async (deviceId = null) => {
    const response = await apiClient.get('/api/realtime/sensor-status', {
      params: deviceId ? { device_id: deviceId } : {}
    });
    return response.data;
  },

  /**
   * 최신 센서 데이터 조회 (분석 없이)
   */
  getLatestSensorData: async () => {
    const response = await apiClient.get('/api/realtime/latest-sensor-data');
    return response.data;
  },

  /**
   * NCPMS 병해충 정보 조회 (테스트용)
   * @param {string} diseaseName - 병해충 한글명
   */
  getNCPMSDiseaseInfo: async (diseaseName) => {
    const response = await apiClient.get(`/api/dummy/test-ncpms/${encodeURIComponent(diseaseName)}`);
    return response.data;
  },

  /**
   * 센서 데이터 + AI 분석 통합 엔드포인트
   * @param {Object} sensorData - 센서 데이터
   * @param {string} cropType - 작물 종류
   * @param {string} userContext - 사용자 컨텍스트
   */
  analyzeSensorData: async (sensorData, cropType = 'tomato', userContext = null) => {
    const response = await apiClient.post('/api/sensor/analyze', sensorData, {
      params: { 
        crop_type: cropType,
        user_context: userContext
      }
    });
    return response.data;
  },
};

/**
 * 작물 한글명 -> 영문 코드 매핑
 */
export const CROP_MAP = {
  '딸기': 'strawberry',
  '토마토': 'tomato',
  '상추': 'lettuce',
  '배추': 'cabbage',
};

/**
 * 더미 센서 데이터 생성 헬퍼
 * @param {string} deviceId - 디바이스 ID
 */
export const generateDummySensorData = (deviceId = 'ESP32_FRONTEND_001') => {
  return {
    device_id: deviceId,
    temperature: Math.random() * 10 + 20, // 20-30°C
    humidity: Math.random() * 20 + 50, // 50-70%
    soil_moisture: Math.random() * 20 + 40, // 40-60%
    light_intensity: Math.random() * 30000 + 20000, // 20000-50000 lux
    co2_level: Math.random() * 400 + 600, // 600-1000 ppm
    timestamp: new Date().toISOString(),
  };
};

export default api;
