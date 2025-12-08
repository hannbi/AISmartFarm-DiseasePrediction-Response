/**
 * 센서 데이터 분석 커스텀 훅
 * 
 * 센서 데이터 조회 및 AI 분석을 관리하는 React Hook
 */

import { useState, useEffect, useCallback } from 'react';
import api, { CROP_MAP, generateDummySensorData } from '../services/api';

/**
 * 센서 데이터 분석 훅
 * @param {Object} options - 옵션
 * @param {string} options.cropName - 작물 한글명 (딸기, 토마토, 상추, 배추)
 * @param {Array<string>} options.equipmentList - 장비 목록
 * @param {boolean} options.autoFetch - 자동 조회 여부
 * @param {number} options.refreshInterval - 자동 새로고침 간격 (ms)
 * @param {boolean} options.useDummyData - 더미 데이터 사용 여부
 */
export function useSensorAnalysis({
  cropName = '토마토',
  equipmentList = [],
  autoFetch = false,
  refreshInterval = 60000, // 1분
  useDummyData = true, // 기본적으로 더미 데이터 사용
} = {}) {
  const [sensorData, setSensorData] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // 작물 영문 코드 변환
  const cropType = CROP_MAP[cropName] || 'tomato';

  /**
   * 센서 데이터 조회
   */
  const fetchSensorData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      let data;
      if (useDummyData) {
        // 더미 데이터 생성
        data = generateDummySensorData();
      } else {
        // 실제 센서 데이터 조회
        data = await api.getLatestSensorData();
      }

      setSensorData(data);
      setLastUpdated(new Date());
      return data;
    } catch (err) {
      console.error('센서 데이터 조회 실패:', err);
      setError(err.response?.data?.detail || err.message || '센서 데이터 조회 실패');
      
      // 에러 시 더미 데이터로 폴백
      if (!useDummyData) {
        const dummyData = generateDummySensorData();
        setSensorData(dummyData);
        return dummyData;
      }
      return null;
    } finally {
      setLoading(false);
    }
  }, [useDummyData]);

  /**
   * AI 분석 실행
   */
  const analyzeData = useCallback(async (customSensorData = null, additionalInfo = null) => {
    try {
      setLoading(true);
      setError(null);

      // 센서 데이터 준비 (전달받은 데이터 우선, 없으면 현재 상태 또는 새로 조회)
      let dataToAnalyze = customSensorData || sensorData;
      
      if (!dataToAnalyze) {
        dataToAnalyze = await fetchSensorData();
      }

      if (!dataToAnalyze) {
        throw new Error('분석할 센서 데이터가 없습니다');
      }

      let result;
      
      if (useDummyData) {
        // 더미 데이터 분석 API 사용
        const payload = {
          sensor_data: dataToAnalyze,
          crop_type: cropType,
          equipment_list: equipmentList,
          user_context: additionalInfo,
        };

        result = await api.analyzeDummyData(payload);
      } else {
        // 실시간 센서 분석 API 사용
        const payload = {
          crop_type: cropType,
          equipment_list: equipmentList,
          farm_location: '스마트팜',
          additional_info: additionalInfo,
        };

        result = await api.analyzeRealtimeData(payload);
        
        // 실시간 API는 sensor_data와 analysis를 분리해서 반환
        if (result.sensor_data) {
          setSensorData(result.sensor_data);
        }
        if (result.analysis) {
          result = result.analysis; // analysis 부분만 사용
        }
      }

      setAnalysisResult(result);
      setLastUpdated(new Date());
      return result;
    } catch (err) {
      console.error('AI 분석 실패:', err);
      setError(err.response?.data?.detail || err.message || 'AI 분석 실패');
      return null;
    } finally {
      setLoading(false);
    }
  }, [sensorData, cropType, equipmentList, useDummyData, fetchSensorData]);

  /**
   * 데이터 초기화
   */
  const resetData = useCallback(() => {
    setSensorData(null);
    setAnalysisResult(null);
    setError(null);
    setLastUpdated(null);
  }, []);

  /**
   * 자동 조회 설정
   */
  useEffect(() => {
    if (autoFetch) {
      fetchSensorData();

      if (refreshInterval > 0) {
        const interval = setInterval(fetchSensorData, refreshInterval);
        return () => clearInterval(interval);
      }
    }
  }, [autoFetch, refreshInterval, fetchSensorData]);

  return {
    // 상태
    sensorData,
    analysisResult,
    loading,
    error,
    lastUpdated,
    
    // 액션
    fetchSensorData,
    analyzeData,
    resetData,
    
    // 유틸
    cropType,
  };
}

/**
 * 센서 상태 확인 훅
 */
export function useSensorStatus() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const checkStatus = useCallback(async (deviceId = null) => {
    try {
      setLoading(true);
      setError(null);
      
      const statusData = await api.getSensorStatus(deviceId);
      setStatus(statusData);
      return statusData;
    } catch (err) {
      console.error('센서 상태 확인 실패:', err);
      setError(err.response?.data?.detail || err.message || '센서 상태 확인 실패');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    status,
    loading,
    error,
    checkStatus,
  };
}

export default useSensorAnalysis;
