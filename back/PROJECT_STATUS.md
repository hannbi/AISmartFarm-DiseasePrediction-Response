# 프로젝트 현황 (Project Status)

**작성일**: 2025-12-08  
**브랜치**: feature/backend  
**프로젝트**: AI Smart Farm Backend - 병해 예측 및 생육 환경 분석 시스템

---

## 📊 전체 개요

ESP32 센서 데이터를 수신하여 RAG 기반 GPT-4로 작물 생육 환경을 평가하고 질병 발생 확률을 예측하는 FastAPI 백엔드 시스템입니다.

**핵심 플로우**:
1. 프론트엔드 → 센서 데이터 (더미/실제)
2. 백엔드 → 전처리 및 상태 분석
3. 백엔드 → LLM (RAG) 분석 요청
4. LLM → 생육 환경 점수 + 질병 예측 (병해충명)
5. 백엔드 → NCPMS API로 병해충 이미지/정보 조회
6. 백엔드 → 프론트엔드로 통합 결과 반환

**핵심 기능**:
- 센서 데이터 수신 및 전처리
- 생육 환경 점수화 (0-100점)
- 질병 발생 확률 예측 (% 단위)
- **NCPMS 병해충 이미지 및 상세정보 연동**
- RAG 기반 맞춤형 권장 조치 제공

---

## ✅ 구현 완료 사항

### 1. 프로젝트 구조 ✅

```
back/
├── main.py                      # FastAPI 앱 진입점 ✅
├── requirements.txt             # 의존성 관리 ✅
├── .env.example                 # 환경변수 템플릿 ✅
├── .gitignore                   # Git 제외 파일 ✅
├── .dockerignore                # Docker 제외 파일 ✅
│
├── Dockerfile                   # 개발용 Docker 이미지 ✅
├── Dockerfile.prod              # 프로덕션 Docker 이미지 ✅
├── docker-compose.yml           # 개발 환경 ✅
├── docker-compose.prod.yml      # 프로덕션 환경 ✅
│
├── README.md                    # 프로젝트 문서 ✅
├── API_SPEC.md                  # API 상세 명세 ✅
├── DOCKER.md                    # Docker 가이드 ✅
│
├── app/
    ├── core/
    │   └── config.py            # 환경 설정 관리 ✅
    ├── models/
    │   ├── sensor.py            # 데이터 모델 ✅
    │   └── realtime.py          # 실시간 분석 모델 ✅
    ├── services/
    │   ├── preprocessing.py     # 센서 데이터 전처리 ✅
    │   ├── ai_service.py        # AI/RAG 분석 서비스 ✅
    │   ├── ncpms_service.py     # NCPMS API 연동 서비스 ✅
    │   └── esp32_service.py     # ESP32 센서 연동 서비스 ✅
    └── api/routes/
        ├── health.py            # 헬스체크 API ✅
        ├── sensor.py            # 센서 데이터 API ✅
        ├── dummy.py             # 더미 데이터 테스트 API ✅
        └── realtime.py          # 실시간 ESP32 센서 API ✅
```

---

### 2. 핵심 모듈 구현 상태

#### 2.1 데이터 모델 (`app/models/sensor.py`, `app/models/realtime.py`) ✅

| 모델명 | 상태 | 설명 |
|--------|------|------|
| `SensorData` | ✅ 완료 | ESP32 원본 센서 데이터 (온도, 습도, 토양습도, 조도, CO2) |
| `ProcessedSensorData` | ✅ 완료 | 전처리된 데이터 + 상태 분석 결과 |
| `GrowthEnvironmentScore` | ✅ 완료 | 생육 환경 평가 (점수, 상태, 상세) |
| `DiseaseInfo` | ✅ 완료 | 질병 정보 (이름, 확률, 원인, 증상, 예방법, **NCPMS 데이터**) |
| `AIAnalysisRequest` | ✅ 완료 | AI 분석 요청 모델 |
| `AIAnalysisResponse` | ✅ 완료 | AI 분석 응답 모델 (통합) |
| `AnalysisRequest` | ✅ 완료 | **실시간 분석 요청** (작물, 장비, 위치) |
| `RealTimeAnalysisResponse` | ✅ 완료 | **실시간 분석 응답** (센서 데이터 + 분석 결과) |

**주요 필드**:
```python
# 생육 환경 평가
- overall_score: 0-100점 (전체 점수)
- status: 최적/양호/주의/불량
- temperature_score, humidity_score, soil_moisture_score

# 질병 예측
- diseases: 확률 순 정렬된 질병 리스트
- probability: 발생 확률 (%)
- reason, symptoms, prevention
```

#### 2.2 전처리 서비스 (`app/services/preprocessing.py`) ✅

| 기능 | 상태 | 설명 |
|------|------|------|
| 데이터 검증 | ✅ 완료 | Pydantic 모델 기반 자동 검증 |
| 상태 분석 | ✅ 완료 | 온도/습도 정상/경고/위험 판단 |
| 작물별 최적 조건 | ✅ 완료 | default, tomato 조건 설정 |
| LLM 포맷팅 | ✅ 완료 | AI 분석용 텍스트 생성 |

**구현된 기능**:
- `validate_and_clean()`: 센서 데이터 검증
- `analyze_status()`: 값의 상태 분석 (정상/경고/위험)
- `process()`: 센서 데이터 전처리 및 상태 분석
- `format_for_llm()`: LLM 입력용 포맷팅

**작물별 최적 조건** (확장 가능):
```python
OPTIMAL_CONDITIONS = {
    "default": {온도: 18-28°C, 습도: 50-70%, 토양습도: 40-60%},
    "tomato": {온도: 20-30°C, 습도: 50-70%, 토양습도: 40-60%}
}
```

#### 2.3 AI 분석 서비스 (`app/services/ai_service.py`) ✅

| 기능 | 상태 | 설명 |
|------|------|------|
| OpenAI GPT-4 연동 | ✅ 완료 | API 호출 및 응답 처리 |
| 시스템 프롬프트 | ✅ 완료 | 작물별 맞춤 프롬프트 생성 |
| 생육 환경 평가 | ✅ 완료 | 0-100점 점수화 요청 |
| 질병 확률 예측 | ✅ 완료 | 확률 순 정렬 요청 |
| JSON 파싱 | ✅ 완료 | 구조화된 응답 파싱 |
| Fallback 처리 | ✅ 완료 | 파싱 실패 시 기본 응답 |
| NCPMS 데이터 통합 | ✅ 완료 | 병해충 이미지/정보 보강 |

**AI 분석 프로세스**:
1. 작물별 시스템 프롬프트 생성
2. 센서 데이터 + 사용자 컨텍스트 결합
3. OpenAI API 호출 (temperature=0.7, max_tokens=1500)
4. JSON 응답 파싱 (growth_environment, diseases, recommendations)
5. **각 질병명으로 NCPMS API 호출하여 이미지 및 상세정보 조회**
6. LLM 결과 + NCPMS 데이터 통합
7. 실패 시 fallback 응답 생성
| 엔드포인트 | 메서드 | 상태 | 설명 |
|-----------|--------|------|------|
| `/api/health` | GET | ✅ 완료 | 서버 헬스체크 |
| `/api/sensor/data` | POST | ✅ 완료 | 센서 데이터 전처리만 수행 |
| `/api/sensor/analyze` | POST | ✅ 완료 | 센서 데이터 → AI 분석 (통합) |
| `/api/sensor/analyze-processed` | POST | ✅ 완료 | 전처리 완료 데이터 → AI 분석 |
| `/api/dummy/analyze-dummy` | POST | ✅ 완료 | **더미 데이터 테스트 (프론트용)** |
| `/api/dummy/test-ncpms/{disease}` | GET | ✅ 완료 | **NCPMS API 테스트** |

**더미 데이터 테스트 API** (`/api/dummy/analyze-dummy`):
- 프론트엔드에서 더미 센서 데이터 전송
- 전체 플로우 테스트 (전처리 → LLM → NCPMS 통합)
- LLM 분석 결과 + 병해충 이미지/정보 반환
- 실제 센서 연동 전 프론트 개발용

**주요 API 흐름**:료 | LLM 결과에 NCPMS 데이터 통합 |
| 병해충명 매핑 | ✅ 완료 | 한글명 → API 코드 변환 |

**지원 병해충**:
- 잿빛곰팡이병 (상세 정보, 이미지, 방제법)
- 역병 (상세 정보, 이미지, 방제법)
- 탄저병 (상세 정보, 이미지, 방제법)
- 흰가루병, 노균병, 시들음병 등 (매핑 준비)

**반환 정보**:
- 학명 (scientific_name)
- 병해충 이미지 URL 목록 (최대 3개)
- 상세 증상 목록
- 방제 정보 (예방법, 치료법)
- 참고 URL

#### 2.5 ESP32 연동 서비스 (`app/services/esp32_service.py`) ✅

| 기능 | 상태 | 설명 |
|------|------|------|
| 센서 데이터 수집 | ✅ 완료 | ESP32 디바이스에서 센서 데이터 회수 |
| 모크 데이터 생성 | ✅ 완료 | 개발 환경용 모크 센서 데이터 제공 |
| 디바이스 상태 확인 | ✅ 완료 | ESP32 연결 상태 및 헬스체크 |
| Fallback 메커니즘 | ✅ 완료 | 연결 실패 시 모크 데이터로 자동 대체 |

**구현된 기능**:
- `fetch_sensor_data()`: ESP32로부터 센서 데이터 비동기 회수
- `_get_mock_sensor_data()`: 현실적인 모크 데이터 생성
  - 온도: 15-30℃ (random)
  - 습도: 40-70% (random)
  - 토양습도: 30-60% (random)
  - 조도: 10000-60000 lux (random)
  - CO2: 400-1200 ppm (random)
- `get_device_status()`: 디바이스 연결 상태 확인

**환경 설정**:
- `ESP32_ENDPOINT`: ESP32 디바이스 엔드포인트 URL (.env 설정)
- 엔드포인트 미설정 시 자동으로 모크 데이터 사용

#### 2.6 API 엔드포인트 (`app/api/routes/`) ✅

| 엔드포인트 | 메서드 | 상태 | 설명 |
|-----------|--------|------|------|
| `/api/health` | GET | ✅ 완료 | 서버 헬스체크 |
| `/api/sensor/data` | POST | ✅ 완료 | 센서 데이터 전처리만 수행 |
| `/api/sensor/analyze` | POST | ✅ 완료 | 센서 데이터 → AI 분석 (통합) |
| `/api/sensor/analyze-processed` | POST | ✅ 완료 | 전처리 완료 데이터 → AI 분석 |
| `/api/dummy/analyze-dummy` | POST | ✅ 완료 | **더미 데이터 테스트 (프론트용)** |
| `/api/dummy/test-ncpms/{disease}` | GET | ✅ 완료 | **NCPMS API 테스트** |
| `/api/realtime/analyze-realtime` | POST | ✅ 완료 | **실시간 센서 분석 (프로덕션용)** |
| `/api/realtime/sensor-status` | GET | ✅ 완료 | **ESP32 디바이스 상태 확인** |
| `/api/realtime/latest-sensor-data` | GET | ✅ 완료 | **최신 센서 데이터 조회** |

**두 가지 분석 시나리오**:

1. **더미 데이터 (`/api/dummy`)**:
   - 프론트엔드에서 센서 데이터 직접 전송
   - 전체 플로우 테스트 (전처리 → LLM → NCPMS)
   - ESP32 연동 전 개발 및 테스트용

2. **실시간 센서 (`/api/realtime`)**:
   - 프론트엔드는 작물 정보만 전송
   - 백엔드가 ESP32에서 센서 데이터 자동 수집
   - 센서 데이터 + 분석 결과 모두 반환
   - ESP32 연동 완료 후 프로덕션용

**주요 API 흐름 (더미)**:미)**:
```
ESP32 센서 데이터 (프론트가 전송)
    ↓
POST /api/dummy/analyze-dummy
    ↓
1. 데이터 검증 (Pydantic)
2. 전처리 & 상태 분석
3. LLM 포맷 생성
4. GPT-4 RAG 분석
5. NCPMS API 호출 (병해충별)
6. 데이터 통합 (LLM + NCPMS)
    ↓
JSON 응답 (생육 환경 점수 + 질병 확률 + 이미지)
    ↓
React 프론트엔드
```

**주요 API 흐름 (실시간)**:
```
프론트엔드 (작물 정보만 전송)
    ↓
POST /api/realtime/analyze-realtime
    ↓
1. ESP32 디바이스에서 센서 데이터 수집
2. 데이터 검증 (Pydantic)
3. 전처리 & 상태 분석
4. LLM 포맷 생성
5. GPT-4 RAG 분석
6. NCPMS API 호출 (병해충별)
7. 데이터 통합 (LLM + NCPMS)
    ↓
JSON 응답 (센서 데이터 + 분석 결과 + 이미지)
    ↓
React 프론트엔드
```

#### 2.7 설정 관리 (`app/core/config.py`) ✅

| 설정 항목 | 상태 | 설명 |
|-----------|------|------|
| OpenAI API | ✅ 완료 | API 키, 모델 설정 |
| NCPMS API | ✅ 완료 | 국가농작물병해충관리시스템 API 키 |
| 서버 설정 | ✅ 완료 | HOST, PORT, DEBUG |
| CORS 설정 | ✅ 완료 | 허용 오리진 관리 |
| ESP32 엔드포인트 | ✅ 완료 | ESP32 디바이스 URL 설정 |
```
┌─────────────┐
│   ESP32     │ 센서 데이터 전송
│  (센서)     │ (온도, 습도, 토양습도, 조도, CO2)
└──────┬──────┘
       │
       ↓ POST /api/sensor/analyze (또는 /api/dummy/analyze-dummy)
┌─────────────────────────────────────────┐
│    FastAPI Backend                       │
│  ┌────────────────────────────────────┐ │
│  │ 1. 데이터 검증 (Pydantic)         │ │
│  │    - 온도: -50~100°C              │ │
│  │    - 습도: 0~100%                 │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │ 2. 전처리 & 상태 분석             │ │
│  │    - 정상/경고/위험 판단          │ │
│  │    - 작물별 최적 조건 비교        │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │ 3. AI 분석 (GPT-4 RAG)           │ │
│  │    - 생육 환경 점수 (0-100)      │ │
│  │    - 질병 확률 예측 (%)          │ │
│  │    - 병해충명 추출               │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │ 4. NCPMS API 호출 (병해충별)     │ │
│  │    - 병해충 이미지 (3장)         │ │
│  │    - 학명, 증상, 방제법          │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │ 5. 데이터 통합                    │ │
│  │    - LLM 분석 + NCPMS 정보       │ │
│  └────────────────────────────────────┘ │
└─────────────┬───────────────────────────┘
              │
              ↓ JSON Response
┌─────────────────────────────────────────┐
│  React Frontend                          │
│  - 생육 환경 점수 시각화                │
│  - 질병 확률 차트                       │
│  - 병해충 이미지 갤러리                 │
│  - 상세 증상 및 방제법 표시             │
│  - 권장 조치 알림                       │
└─────────────────────────────────────────┘
```───────────┐
│   ESP32     │ 센서 데이터 전송
│  (센서)     │ (온도, 습도, 토양습도, 조도, CO2)
└──────┬──────┘
       │
       ↓ POST /api/sensor/analyze
┌─────────────────────────────────────┐
│    FastAPI Backend                   │
│  ┌────────────────────────────────┐ │
│  │ 1. 데이터 검증 (Pydantic)      │ │
│  │    - 온도: -50~100°C          │ │
│  │    - 습도: 0~100%             │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │ 2. 전처리 & 상태 분석          │ │
│  │    - 정상/경고/위험 판단       │ │
│  │    - 작물별 최적 조건 비교     │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │ 3. AI 분석 (GPT-4 RAG)        │ │
│  │    - 생육 환경 점수 (0-100)   │ │
│  │    - 질병 확률 예측 (%)       │ │
│  │    - 맞춤형 권장 조치         │ │
│  └────────────────────────────────┘ │
└─────────────┬───────────────────────┘
              │
              ↓ JSON Response
┌─────────────────────────────────────┐
│  React Frontend                      │
│  - 생육 환경 점수 시각화             │
│  - 질병 확률 차트                    │
│  - 권장 조치 표시                    │
└─────────────────────────────────────┘
```

      "probability": 68.5,
      "reason": "습도 70% 이상 유지, 환기 부족",
      "symptoms": "잎과 줄기에 회색 곰팡이 발생",
      "prevention": "습도 관리 및 환기 강화",
      "scientific_name": "Botrytis cinerea",
      "images": [
        "https://ncpms.rda.go.kr/images/disease_001.jpg",
        "https://ncpms.rda.go.kr/images/disease_002.jpg",
        "https://ncpms.rda.go.kr/images/disease_003.jpg"
      ],
      "detailed_symptoms": [
        "잎과 줄기에 회갈색 병반 발생",
        "습한 조건에서 회색 곰팡이 형성",
        "과실에 수침상 병반 발생 후 곰팡이 증식"
      ],
      "management": {
        "prevention": [
          "적정 재식 거리 유지로 통풍 개선",
          "시설 내 환기 철저",
          "질소질 비료 과다 시용 지양"
        ],
        "treatment": [
          "등록된 살균제 살포 (펜헥사미드, 이프로디온 등)",
          "병 발생 초기 집중 방제"
        ]
      },
      "reference_url": "https://ncpms.rda.go.kr",
      "source": "국가농작물병해충관리시스템"
    }, 분석 응답 예시

```json
{
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
  "analysis_summary": "토마토 생육 환경은 전반적으로 양호하나...",
  "timestamp": "2025-12-08T10:30:00"
}
```

---

## ❌ 미구현 사항

### 1. 데이터 저장 (선택사항) ⏳
- [ ] 로컬 파일 기반 히스토리 저장 (JSON/CSV)
- [ ] 센서 데이터 로깅
- [ ] 분석 결과 기록

### 2. 캐싱 (선택사항) ⏳
- [ ] 메모리 기반 캐싱
- [ ] API 응답 캐싱

### 3. 단일 사용자 관리 ⏳
- [ ] 기본 설정 관리 (작물 종류, 디바이스 설정)
- [ ] 사용자 선호 설정

### 4. 실시간 기능 ⏳
- [ ] WebSocket 연동 (선택사항)
- [ ] 센서 데이터 실시간 스트리밍
- [ ] 브라우저 알림 (위험도 높을 시)

### 5. 데이터 분석 고도화 ⏳
- [ ] 센서 데이터 트렌드 분석 (단기 메모리 기반)
- [ ] 이상치 감지
- [ ] 작물 생육 단계별 분석

### 6. RAG 시스템 고도화 ⏳
- [ ] Vector DB 연동 (Pinecone, Weaviate)
- [ ] 농업 전문 문서 임베딩
- [ ] Fine-tuning 데이터 수집
- [ ] 한국 농업 환경 최적화

### 7. 확장 기능 ⏳
- [ ] 다국어 지원 (i18n)
- [ ] 간단한 로깅 시스템 (파일 기반)
- [ ] 모니터링 대시보드 (간소화)

### 8. 테스트 ⏳
- [ ] Unit Tests (pytest)
- [ ] Integration Tests
- [ ] API Tests
- [ ] Load Tests (Locust)

### 9. CI/CD ⏳
- [ ] GitHub Actions
- [ ] 자동 배포
- [ ] 코드 품질 검사 (pylint, black)
- [ ] 보안 스캔

### 10. 배포 최적화 ⏳
- [ ] SSL/TLS 인증서 (Let's Encrypt)
- [ ] 리버스 프록시 최적화 (Nginx)
- [ ] Docker 이미지 최적화

---

## 🔧 기술 스택

### 구현 완료 ✅
- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn 0.27.0 (개발), Gunicorn 21.2.0 (프로덕션)
- **AI**: OpenAI GPT-4
- **Validation**: Pydantic 2.5.3
- **Environment**: python-dotenv 1.0.0
- **HTTP**: httpx 0.26.0, requests 2.31.0
- **Data**: pandas 2.1.4, numpy 1.26.3
- **Container**: Docker, Docker Compose

### 준비 완료 (설정만) 🟡
- **Reverse Proxy**: Nginx (docker-compose.prod.yml)

### 선택사항 (필요시 추가) ⚪
- 로컬 파일 기반 데이터 저장 (JSON/CSV)
- 메모리 캐싱
- Vector DB (RAG 고도화 시)

---

## 🎯 다음 단계 우선순위

### Phase 1: 핵심 기능 테스트 & 안정화 (1주)
1. ✅ ~~Docker 환경 구축~~
2. ✅ ~~더미 데이터 API 구현~~
3. ✅ ~~실시간 센서 API 구현~~
4. ✅ ~~ESP32 서비스 구현 (모크 데이터 포함)~~
5. ⏳ ESP32 센서 연동 테스트
6. ⏳ 기본 테스트 코드 작성
7. ⏳ 에러 처리 강화

### Phase 2: 프론트엔드 연동 (1-2주)
5. ⏳ React 프론트엔드 API 연동
6. ⏳ 실시간 데이터 표시
7. ⏳ 차트 및 시각화

### Phase 3: 데이터 기록 (선택사항, 1주)
8. ⏳ 로컬 파일 기반 히스토리 저장
9. ⏳ 간단한 통계 기능
10. ⏳ CSV 내보내기

### Phase 4: RAG 고도화 (1-2주)
11. ⏳ 작물별 최적 조건 데이터 확장
12. ⏳ 농업 전문 지식 프롬프트 개선
13. ⏳ 질병 데이터베이스 확장

### Phase 5: 배포 & 운영 (1주)
14. ⏳ 프로덕션 배포 (Docker)
15. ⏳ 간단한 로깅
16. ⏳ SSL 인증서 설정

---

## 📞 현재 시스템 테스트 방법

### 1. Docker로 실행

```powershell
# 환경 변수 설정
Copy-Item .env.example .env
# .env 파일에 OPENAI_API_KEY 입력

# 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f backend
```

### 2. API 테스트

```powershell
# 헬스체크
curl http://localhost:8000/api/health

# 센서 데이터 분석
curl -X POST "http://localhost:8000/api/sensor/analyze?crop_type=tomato" `
  -H "Content-Type: application/json" `
  -d '{
    "device_id": "ESP32_001",
    "temperature": 25.5,
    "humidity": 65.0,
    "soil_moisture": 45.0,
    "light_intensity": 5000.0,
    "co2_level": 800.0
  }'
```

### 3. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📝 주요 파일 위치

### 설정 파일
- `back/.env`: 환경 변수 (Git 제외)
- `back/.env.example`: 환경 변수 템플릿
- `back/app/core/config.py`: 설정 관리 클래스

### 코어 로직
- `back/app/models/sensor.py`: 데이터 모델 정의
- `back/app/services/preprocessing.py`: 전처리 로직
- `back/app/services/ai_service.py`: AI 분석 로직
- `back/app/api/routes/sensor.py`: API 엔드포인트

### Docker 관련
- `back/Dockerfile`: 개발용 이미지
- `back/Dockerfile.prod`: 프로덕션 이미지
- `back/docker-compose.yml`: 개발 환경
- `back/docker-compose.prod.yml`: 프로덕션 환경

### 문서
- `back/README.md`: 프로젝트 개요
- `back/API_SPEC.md`: API 명세서
- `back/DOCKER.md`: Docker 가이드
- `back/PROJECT_STATUS.md`: 이 문서

---

**마지막 업데이트**: 2025-12-08  
**작성자**: AI Smart Farm Team  
**버전**: 1.2.0
