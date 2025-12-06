# AI Smart Farm Backend

FastAPI 기반 스마트팜 백엔드 서버 - ESP32 센서 데이터 수신 및 RAG 기반 병해 예측 시스템

## 📋 주요 기능

- **ESP32 센서 데이터 수신**: 온도, 습도, 토양 습도, 조도, CO2 농도 등
- **데이터 전처리**: 센서 데이터 검증, 정제 및 상태 분석
- **생육 환경 평가**: 작물별 최적 생육 조건 대비 현재 환경 점수화 (0-100점)
- **질병 발생 확률 예측**: 현재 환경 기반 질병 발생 가능성을 확률(%)로 예측 및 정렬
- **RAG 기반 AI 분석**: OpenAI GPT를 활용한 맞춤형 병해 예측 및 솔루션 제공
- **React 프론트엔드 연동**: CORS 설정 및 RESTful API 제공

## 🏗️ 프로젝트 구조

```
back/
├── main.py                 # FastAPI 애플리케이션 진입점
├── requirements.txt        # Python 의존성
├── .env.example           # 환경변수 예시
├── .gitignore
├── README.md
└── app/
    ├── __init__.py
    ├── core/              # 핵심 설정
    │   ├── __init__.py
    │   └── config.py      # 환경 설정
    ├── models/            # 데이터 모델
    │   ├── __init__.py
    │   └── sensor.py      # 센서 데이터 모델
    ├── services/          # 비즈니스 로직
    │   ├── __init__.py
    │   ├── preprocessing.py   # 데이터 전처리
    │   └── ai_service.py      # AI/RAG 서비스
    └── api/               # API 라우터
        ├── __init__.py
        └── routes/
            ├── __init__.py
            ├── health.py   # 헬스체크
            └── sensor.py   # 센서 데이터 엔드포인트
```

## 🚀 시작하기

### 1. 가상환경 생성 및 활성화

```powershell
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
.\venv\Scripts\Activate.ps1
```

### 2. 의존성 설치

```powershell
pip install -r requirements.txt
```

### 3. 환경변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 필요한 값을 입력하세요.

```powershell
Copy-Item .env.example .env
```

`.env` 파일 수정:
```env
OPENAI_API_KEY=your_actual_api_key_here
OPENAI_MODEL=gpt-4
HOST=0.0.0.0
PORT=8000
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 4. 서버 실행

```powershell
# 개발 모드 (자동 리로드)
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 다음 URL에서 확인할 수 있습니다:
- API 문서: http://localhost:8000/docs
- 대체 API 문서: http://localhost:8000/redoc

## 📡 API 엔드포인트

### 1. 헬스체크
```http
GET /api/health
```

**응답:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-06T10:30:00",
  "service": "AI Smart Farm Backend"
}
```

---

### 2. 센서 데이터 수신 및 전처리
```http
POST /api/sensor/data
Content-Type: application/json

{
  "device_id": "ESP32_001",
  "temperature": 25.5,
  "humidity": 65.0,
  "soil_moisture": 45.0,
  "light_intensity": 5000.0,
  "co2_level": 800.0
}
```

**Query Parameters:**
- `crop_type` (optional): 작물 종류 (default: "default")

**응답:** `ProcessedSensorData`
```json
{
  "device_id": "ESP32_001",
  "temperature": 25.5,
  "humidity": 65.0,
  "soil_moisture": 45.0,
  "light_intensity": 5000.0,
  "co2_level": 800.0,
  "timestamp": "2025-12-06T10:30:00",
  "temperature_status": "정상",
  "humidity_status": "경고",
  "overall_status": "경고"
}
```

---

### 3. 통합 분석 (센서 데이터 → AI 분석)
```http
POST /api/sensor/analyze
Content-Type: application/json

{
  "device_id": "ESP32_001",
  "temperature": 25.5,
  "humidity": 65.0,
  "soil_moisture": 45.0,
  "light_intensity": 5000.0,
  "co2_level": 800.0
}

Query Parameters:
- crop_type: 작물 종류 (예: tomato, lettuce, cucumber)
- user_context: 추가 정보
```

**응답 예시:**
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
    },
    {
      "name": "탄저병",
      "probability": 25.5,
      "reason": "높은 습도와 온도",
      "symptoms": "잎에 갈색 반점 발생",
      "prevention": "적절한 온습도 유지"
    }
  ],
  "risk_level": "중간",
  "recommendations": [
    "환기를 통해 습도를 60% 이하로 낮추세요",
    "물 주기를 줄이고 토양 배수를 확인하세요",
    "예방적 살균제 살포를 고려하세요",
    "작물 간 간격을 확보하여 통풍을 개선하세요"
  ],
  "optimal_conditions": {
    "temperature": "20-25°C",
    "humidity": "50-60%",
    "soil_moisture": "40-50%"
  },
  "analysis_summary": "토마토 생육 환경은 전반적으로 양호하나, 높은 습도로 인해 곰팡이성 질병 발생 위험이 있습니다. 환기를 강화하고 습도 관리에 주의가 필요합니다.",
  "timestamp": "2025-12-06T10:30:00"
}
```

## 🔧 개발 가이드

### 데이터 플로우

1. **ESP32** → 센서 데이터 전송 (온도, 습도, 토양습도, 조도, CO2)
2. **Backend (FastAPI)** → 데이터 수신 및 검증 (Pydantic 모델)
3. **Preprocessing Service** → 데이터 전처리 및 상태 분석
4. **AI Service (RAG + GPT)** → 
   - 생육 환경 평가 (0-100점 점수화)
   - 질병 발생 확률 예측 (확률 순 정렬)
   - 맞춤형 권장 조치 생성
5. **Backend** → React 프론트엔드에 JSON 응답 전달

### 주요 컴포넌트

#### 1. **SensorDataPreprocessor** (`app/services/preprocessing.py`)
- 센서 데이터 검증 및 정제
- 작물별 최적 조건과 비교하여 상태 분석
- LLM 입력용 포맷 생성

#### 2. **AIAnalysisService** (`app/services/ai_service.py`)
- OpenAI GPT API를 활용한 RAG 기반 분석
- **생육 환경 평가**: 작물별 최적 조건 대비 현재 환경 점수화
- **질병 예측**: 환경 조건 기반 질병 발생 확률(%) 계산 및 정렬
- 구조화된 JSON 응답 생성

#### 3. **데이터 모델** (`app/models/sensor.py`)
- `SensorData`: ESP32 원본 센서 데이터
- `ProcessedSensorData`: 전처리된 데이터 + 상태 분석
- `GrowthEnvironmentScore`: 생육 환경 평가 결과 (점수 + 상태)
- `DiseaseInfo`: 개별 질병 정보 (이름, 확률, 원인, 증상, 예방법)
- `AIAnalysisResponse`: 최종 AI 분석 결과 (통합 응답)

### AI 분석 응답 구조

```json
{
  // 1. 생육 환경 평가
  "growth_environment": {
    "overall_score": 75.5,           // 전체 점수 (0-100)
    "status": "양호",                 // 최적/양호/주의/불량
    "temperature_score": 85.0,       // 온도 적합도
    "humidity_score": 60.0,          // 습도 적합도
    "soil_moisture_score": 80.0,     // 토양습도 적합도
    "detail": "상세 평가 내용"
  },
  
  // 2. 질병 발생 확률 예측 (확률 순 정렬)
  "diseases": [
    {
      "name": "질병명",
      "probability": 68.5,           // 발생 확률 (%)
      "reason": "발생 원인",
      "symptoms": "주요 증상",
      "prevention": "예방 방법"
    }
  ],
  
  // 3. 종합 평가
  "risk_level": "중간",              // 낮음/중간/높음
  "recommendations": [],             // 권장 조치 사항
  "optimal_conditions": {},          // 최적 환경 조건
  "analysis_summary": "종합 분석 요약",
  "timestamp": "2025-12-06T10:30:00"
}
```

### 점수 기준

- **90-100점**: 최적 - 현재 환경이 해당 작물의 최적 생육 조건
- **70-89점**: 양호 - 생육에 적합하나 일부 개선 가능
- **50-69점**: 주의 - 환경 개선 필요, 질병 발생 주의
- **0-49점**: 불량 - 즉각적인 환경 개선 필요

### 환경별 설정

- 개발: `DEBUG=True`, 로컬 CORS 설정
- 프로덕션: `DEBUG=False`, 특정 도메인만 허용

## 📝 TODO

- [ ] 데이터베이스 연동 (PostgreSQL/MongoDB)
- [ ] 센서 데이터 히스토리 저장 및 트렌드 분석
- [ ] 작물별/생육단계별 최적 조건 데이터베이스 구축
- [ ] 질병 데이터베이스 확장 (증상, 예방법, 치료법)
- [ ] 실시간 알림 시스템 (WebSocket) - 위험도 높을 시 알림
- [ ] 사용자 인증 및 권한 관리
- [ ] RAG 시스템 고도화 (Vector DB 연동, 농업 전문 문서 학습)
- [ ] 배포 설정 (Docker, CI/CD)
- [ ] 센서 데이터 이상치 감지 및 필터링
- [ ] 다국어 지원 (영어, 한국어)

## 🛠️ 기술 스택

- **Framework**: FastAPI
- **AI/ML**: OpenAI GPT-4, RAG
- **Data Validation**: Pydantic
- **HTTP Client**: httpx
- **Data Processing**: pandas, numpy
