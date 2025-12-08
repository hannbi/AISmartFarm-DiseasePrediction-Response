"""
AI Smart Farm Backend API 테스트 스크립트

ESP32 장비 없이 더미 데이터로 전체 플로우를 테스트합니다.
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any


BASE_URL = "http://localhost:8001"


def print_section(title: str):
    """섹션 헤더 출력"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_response(response: requests.Response, show_full: bool = False):
    """API 응답 출력"""
    print(f"\n[Status Code] {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS")
        try:
            data = response.json()
            if show_full:
                print("\n[Response Body]")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                # 요약 출력
                print("\n[Response Summary]")
                if "status" in data:
                    print(f"  Status: {data.get('status')}")
                if "growth_environment" in data:
                    env = data["growth_environment"]
                    print(f"  생육 환경 점수: {env.get('overall_score')}/100 ({env.get('status')})")
                if "diseases" in data and len(data["diseases"]) > 0:
                    print(f"  예측 질병 수: {len(data['diseases'])}개")
                    for i, disease in enumerate(data["diseases"][:3], 1):
                        print(f"    {i}. {disease.get('name')} - {disease.get('probability')}%")
                        if disease.get('images'):
                            print(f"       이미지 수: {len(disease['images'])}개")
                if "sensor_data" in data:
                    sensor = data["sensor_data"]
                    print(f"  센서 데이터: 온도={sensor.get('temperature')}°C, 습도={sensor.get('humidity')}%")
        except Exception as e:
            print(f"  응답 파싱 오류: {e}")
            print(f"  Raw: {response.text[:200]}")
    else:
        print("❌ FAILED")
        print(f"\n[Error Response]")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)


def test_health_check():
    """1. 헬스체크 테스트"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print_response(response, show_full=True)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        print("⚠️  서버가 실행 중인지 확인하세요: docker-compose up -d")
        return False


def test_sensor_preprocessing():
    """2. 센서 데이터 전처리 테스트"""
    print_section("TEST 2: Sensor Data Preprocessing")
    
    sensor_data = {
        "device_id": "ESP32_TEST_001",
        "temperature": 25.5,
        "humidity": 65.0,
        "soil_moisture": 45.0,
        "light_intensity": 5000.0,
        "co2_level": 800.0
    }
    
    print("\n[Request Data]")
    print(json.dumps(sensor_data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/sensor/data",
            json=sensor_data,
            params={"crop_type": "tomato"}
        )
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 요청 실패: {e}")
        return False


def test_dummy_analysis():
    """3. 더미 데이터 전체 분석 테스트 (LLM + NCPMS)"""
    print_section("TEST 3: Dummy Data Analysis (Full Pipeline)")
    
    dummy_request = {
        "sensor_data": {
            "device_id": "ESP32_DUMMY_001",
            "temperature": 28.5,
            "humidity": 75.0,
            "soil_moisture": 55.0,
            "light_intensity": 45000.0,
            "co2_level": 900.0,
            "timestamp": datetime.now().isoformat()
        },
        "crop_type": "tomato",
        "equipment_list": ["LED 조명", "환기 시스템", "관수 시스템"],
        "user_context": "방울토마토, 재배 3주차"
    }
    
    print("\n[Request Data]")
    print(json.dumps(dummy_request, indent=2, ensure_ascii=False))
    
    print("\n⏳ AI 분석 중... (30-60초 소요 예상)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/dummy/analyze-dummy",
            json=dummy_request,
            timeout=120  # 2분 타임아웃
        )
        print_response(response)
        
        # 성공 시 상세 정보 추가 출력
        if response.status_code == 200:
            data = response.json()
            
            print("\n[상세 분석 결과]")
            
            # 생육 환경
            if "growth_environment" in data:
                env = data["growth_environment"]
                print(f"\n📊 생육 환경 평가:")
                print(f"  - 전체 점수: {env.get('overall_score')}/100")
                print(f"  - 상태: {env.get('status')}")
                print(f"  - 온도 점수: {env.get('temperature_score')}/100")
                print(f"  - 습도 점수: {env.get('humidity_score')}/100")
                print(f"  - 토양습도 점수: {env.get('soil_moisture_score')}/100")
                print(f"  - 평가: {env.get('detail', '')[:100]}...")
            
            # 질병 예측
            if "diseases" in data:
                print(f"\n🦠 질병 예측 (총 {len(data['diseases'])}개):")
                for i, disease in enumerate(data["diseases"], 1):
                    print(f"\n  {i}. {disease.get('name')} ({disease.get('probability')}%)")
                    print(f"     원인: {disease.get('reason', '')[:80]}...")
                    print(f"     예방: {disease.get('prevention', '')[:80]}...")
                    if disease.get('scientific_name'):
                        print(f"     학명: {disease.get('scientific_name')}")
                    if disease.get('images'):
                        print(f"     이미지: {len(disease['images'])}개")
                        for img in disease['images'][:2]:
                            print(f"       - {img}")
            
            # 권장 조치
            if "recommendations" in data:
                print(f"\n💡 권장 조치:")
                for i, rec in enumerate(data["recommendations"], 1):
                    print(f"  {i}. {rec}")
            
            # 위험도
            if "risk_level" in data:
                print(f"\n⚠️  전체 위험도: {data['risk_level']}")
        
        return response.status_code == 200
    except requests.Timeout:
        print("❌ 타임아웃: AI 분석이 너무 오래 걸립니다")
        return False
    except Exception as e:
        print(f"❌ 요청 실패: {e}")
        return False


def test_ncpms_api():
    """4. NCPMS API 테스트"""
    print_section("TEST 4: NCPMS API Test")
    
    test_diseases = ["잿빛곰팡이병", "역병", "탄저병"]
    
    for disease in test_diseases:
        print(f"\n[Testing] {disease}")
        try:
            response = requests.get(f"{BASE_URL}/api/dummy/test-ncpms/{disease}")
            print_response(response)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('images'):
                    print(f"  ✓ 이미지 URL 확인: {len(data['images'])}개")
                if data.get('scientific_name'):
                    print(f"  ✓ 학명: {data['scientific_name']}")
        except Exception as e:
            print(f"  ❌ 요청 실패: {e}")


def test_realtime_sensor_status():
    """5. ESP32 센서 상태 확인 (모크 데이터)"""
    print_section("TEST 5: ESP32 Sensor Status (Mock)")
    
    print("⚠️  ESP32 엔드포인트가 설정되지 않아 모크 데이터를 사용합니다.")
    
    try:
        response = requests.get(f"{BASE_URL}/api/realtime/sensor-status")
        print_response(response, show_full=True)
        return response.status_code in [200, 503]  # 503도 정상 (ESP32 없음)
    except Exception as e:
        print(f"❌ 요청 실패: {e}")
        return False


def test_realtime_sensor_data():
    """6. 최신 센서 데이터 조회 (모크 데이터)"""
    print_section("TEST 6: Latest Sensor Data (Mock)")
    
    try:
        response = requests.get(f"{BASE_URL}/api/realtime/latest-sensor-data")
        print_response(response, show_full=True)
        return response.status_code in [200, 503]
    except Exception as e:
        print(f"❌ 요청 실패: {e}")
        return False


def run_all_tests():
    """전체 테스트 실행"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "AI Smart Farm Backend API Test" + " " * 27 + "║")
    print("╚" + "=" * 78 + "╝")
    
    results = {}
    
    # 1. 헬스체크
    results["health"] = test_health_check()
    if not results["health"]:
        print("\n❌ 서버 연결 실패. 테스트를 중단합니다.")
        return
    
    # 2. 센서 전처리
    results["preprocessing"] = test_sensor_preprocessing()
    
    # 3. 더미 데이터 분석 (핵심 테스트)
    results["dummy_analysis"] = test_dummy_analysis()
    
    # 4. NCPMS API
    test_ncpms_api()
    
    # 5-6. 실시간 센서 (모크)
    results["sensor_status"] = test_realtime_sensor_status()
    results["sensor_data"] = test_realtime_sensor_data()
    
    # 결과 요약
    print_section("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n총 테스트: {total}개")
    print(f"성공: {passed}개")
    print(f"실패: {total - passed}개")
    
    print("\n[상세 결과]")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:20s}: {status}")
    
    if passed == total:
        print("\n🎉 모든 테스트 통과!")
    else:
        print("\n⚠️  일부 테스트 실패")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    run_all_tests()
