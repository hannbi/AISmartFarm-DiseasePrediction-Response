# API 명세서

AI Smart Farm Backend API 상세 명세

## 📌 Base URL

```
http://localhost:8000
```

## 🔐 인증

현재 버전은 인증이 구현되어 있지 않습니다. (추후 JWT 기반 인증 추가 예정)

---

## 📡 API 엔드포인트

### 1. Health Check

서버 상태를 확인합니다.

```http
GET /api/health
```

**응답**

```json
{
  "status": "healthy",
  "timestamp": "2025-12-06T10:30:00.123456",
  "service": "AI Smart Farm Backend"
}
```

**상태 코드**
- `200 OK`: 서버 정상 작동

---

### 2. 센서 데이터 수신 및 전처리

ESP32에서 전송된 센서 데이터를 받아 전처리하고 상태를 분석합니다.

```http
POST /api/sensor/data
```

**Query Parameters**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| crop_type | string | No | "default" | 작물 종류 (tomato, lettuce, cucumber 등) |

**Request Body**

```json
{
  "device_id": "ESP32_001",
  "temperature": 25.5,
  "humidity": 65.0,
  "soil_moisture": 45.0,
  "light_intensity": 5000.0,
  "co2_level": 800.0,
  "timestamp": "2025-12-06T10:30:00"  // optional
}
```

**Request Body 필드**

| 필드 | 타입 | 필수 | 범위 | 설명 |
|-----|------|------|------|------|
| device_id | string | Yes | - | ESP32 디바이스 고유 ID |
| temperature | float | Yes | -50 ~ 100 | 온도 (°C) |
| humidity | float | Yes | 0 ~ 100 | 습도 (%) |
| soil_moisture | float | No | 0 ~ 100 | 토양 습도 (%) |
| light_intensity | float | No | ≥ 0 | 조도 (lux) |
| co2_level | float | No | ≥ 0 | CO2 농도 (ppm) |
| timestamp | datetime | No | - | 데이터 수집 시각 (미입력 시 서버 시간) |

**응답 예시**

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

**상태 코드**
- `200 OK`: 정상 처리
- `422 Unprocessable Entity`: 입력 데이터 유효성 오류
- `500 Internal Server Error`: 서버 내부 오류

---

### 3. 통합 분석 (센서 데이터 → AI 분석)

센서 데이터를 받아 전처리 후 AI 분석을 수행하여 생육 환경 평가 및 질병 예측 결과를 반환합니다.

```http
POST /api/sensor/analyze
```

**Query Parameters**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| crop_type | string | No | "default" | 작물 종류 (tomato, lettuce, cucumber 등) |
| user_context | string | No | null | 사용자 추가 정보 (품종, 재배 기간 등) |

**Request Body**

센서 데이터와 동일 (위 2번 참조)

**응답 예시**

```json
{
  "growth_environment": {
    "overall_score": 75.5,
    "status": "양호",
    "temperature_score": 85.0,
    "humidity_score": 60.0,
    "soil_moisture_score": 80.0,
    "detail": "현재 온도는 최적 범위이나, 습도가 다소 높은 상태입니다. 토양 습도는 적절합니다."
  },
  "diseases": [
    {
      "name": "잿빛곰팡이병",
      "probability": 68.5,
      "reason": "습도 70% 이상 유지, 환기 부족, 밤낮 온도차",
      "symptoms": "잎과 줄기에 회색 곰팡이가 발생하며, 과실에도 감염됩니다.",
      "prevention": "습도를 60% 이하로 관리하고, 환기를 강화하세요. 병든 잎은 즉시 제거합니다."
    },
    {
      "name": "역병",
      "probability": 42.0,
      "reason": "토양 과습, 고온다습 환경, 배수 불량",
      "symptoms": "잎이 시들고 갈색으로 변하며, 줄기가 물러집니다.",
      "prevention": "배수 관리를 철저히 하고, 과습을 방지하세요. 감염된 식물은 격리합니다."
    },
    {
      "name": "탄저병",
      "probability": 25.5,
      "reason": "높은 습도와 온도, 밀식 재배",
      "symptoms": "잎에 갈색 반점이 생기고 점차 확대됩니다.",
      "prevention": "적절한 온습도를 유지하고, 작물 간 간격을 충분히 확보하세요."
    }
  ],
  "risk_level": "중간",
  "recommendations": [
    "환기를 통해 습도를 60% 이하로 낮추세요",
    "물 주기를 줄이고 토양 배수 상태를 확인하세요",
    "예방적 살균제 살포를 고려하세요 (잿빛곰팡이병 대응)",
    "작물 간 간격을 확보하여 통풍을 개선하세요",
    "병든 잎이나 과실은 즉시 제거하여 전염을 방지하세요"
  ],
  "optimal_conditions": {
    "temperature": "20-25°C",
    "humidity": "50-60%",
    "soil_moisture": "40-50%",
    "light_intensity": "30000-50000 lux",
    "co2_level": "1000-1500 ppm"
  },
  "analysis_summary": "토마토 생육 환경은 전반적으로 양호합니다(75.5점). 온도는 최적 범위에 있으나, 습도가 다소 높아 곰팡이성 질병(특히 잿빛곰팡이병) 발생 위험이 있습니다. 환기를 강화하고 습도 관리에 주의가 필요합니다.",
  "timestamp": "2025-12-06T10:30:00.123456"
}
```

**응답 필드 상세**

#### `growth_environment` (생육 환경 평가)

| 필드 | 타입 | 범위 | 설명 |
|-----|------|------|------|
| overall_score | float | 0-100 | 전체 생육 환경 점수 |
| status | string | - | 최적(90-100) / 양호(70-89) / 주의(50-69) / 불량(0-49) |
| temperature_score | float | 0-100 | 온도 적합도 점수 |
| humidity_score | float | 0-100 | 습도 적합도 점수 |
| soil_moisture_score | float | 0-100 | 토양 습도 적합도 점수 (센서값 있을 시) |
| detail | string | - | 상세 평가 내용 |

#### `diseases` (질병 예측, 확률 순 정렬)

| 필드 | 타입 | 범위 | 설명 |
|-----|------|------|------|
| name | string | - | 질병명 (한글) |
| probability | float | 0-100 | 발생 확률 (%) |
| reason | string | - | 발생 원인/조건 |
| symptoms | string | - | 주요 증상 |
| prevention | string | - | 예방 방법 |

#### 기타 필드

| 필드 | 타입 | 설명 |
|-----|------|------|
| risk_level | string | 전체 위험도 (낮음/중간/높음) |
| recommendations | array[string] | 권장 조치 사항 (3-5개) |
| optimal_conditions | object | 해당 작물의 최적 환경 조건 |
| analysis_summary | string | 종합 분석 요약 |
| timestamp | datetime | 분석 완료 시각 |

**상태 코드**
- `200 OK`: 정상 처리
- `422 Unprocessable Entity`: 입력 데이터 유효성 오류
- `500 Internal Server Error`: 서버 내부 오류 (AI API 호출 실패 포함)

---

### 4. 전처리된 데이터 분석

이미 전처리가 완료된 센서 데이터에 대해 AI 분석만 수행합니다.

```http
POST /api/sensor/analyze-processed
```

**Request Body**

```json
{
  "sensor_data": {
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
  },
  "crop_type": "tomato",
  "user_context": "방울토마토, 재배 3주차"
}
```

**응답**

3번 API와 동일한 형식

**상태 코드**
- `200 OK`: 정상 처리
- `422 Unprocessable Entity`: 입력 데이터 유효성 오류
- `500 Internal Server Error`: 서버 내부 오류

---

## 📊 데이터 모델

### SensorData

ESP32에서 전송하는 원본 센서 데이터

```typescript
{
  device_id: string;          // 필수
  temperature: float;         // 필수, -50 ~ 100
  humidity: float;            // 필수, 0 ~ 100
  soil_moisture?: float;      // 선택, 0 ~ 100
  light_intensity?: float;    // 선택, >= 0
  co2_level?: float;          // 선택, >= 0
  timestamp?: datetime;       // 선택
}
```

### ProcessedSensorData

전처리된 센서 데이터 + 상태 분석

```typescript
{
  ...SensorData,
  temperature_status: string;  // 정상/경고/위험
  humidity_status: string;     // 정상/경고/위험
  overall_status: string;      // 정상/경고/위험
}
```

### AIAnalysisResponse

AI 분석 최종 결과

```typescript
{
  growth_environment: GrowthEnvironmentScore;
  diseases: DiseaseInfo[];
  risk_level: string;
  recommendations: string[];
  optimal_conditions: object;
  analysis_summary: string;
  timestamp: datetime;
}
```

---

## ⚠️ 에러 응답

### 422 Unprocessable Entity

```json
{
  "detail": [
    {
      "loc": ["body", "temperature"],
      "msg": "ensure this value is greater than or equal to -50",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "분석 중 오류가 발생했습니다: OpenAI API connection failed"
}
```

---

## 🔄 사용 예시

### Python (requests)

```python
import requests

# 센서 데이터 전송 및 분석
url = "http://localhost:8000/api/sensor/analyze"
data = {
    "device_id": "ESP32_001",
    "temperature": 25.5,
    "humidity": 65.0,
    "soil_moisture": 45.0
}
params = {
    "crop_type": "tomato"
}

response = requests.post(url, json=data, params=params)
result = response.json()

print(f"생육 환경 점수: {result['growth_environment']['overall_score']}")
print(f"위험도: {result['risk_level']}")
for disease in result['diseases']:
    print(f"- {disease['name']}: {disease['probability']}%")
```

### JavaScript (fetch)

```javascript
const url = "http://localhost:8000/api/sensor/analyze?crop_type=tomato";
const data = {
  device_id: "ESP32_001",
  temperature: 25.5,
  humidity: 65.0,
  soil_moisture: 45.0
};

fetch(url, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(data)
})
  .then(response => response.json())
  .then(result => {
    console.log("생육 환경 점수:", result.growth_environment.overall_score);
    console.log("위험도:", result.risk_level);
    result.diseases.forEach(disease => {
      console.log(`- ${disease.name}: ${disease.probability}%`);
    });
  });
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/sensor/analyze?crop_type=tomato" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ESP32_001",
    "temperature": 25.5,
    "humidity": 65.0,
    "soil_moisture": 45.0
  }'
```

---

## 📝 변경 이력

### v1.0.0 (2025-12-06)
- 초기 API 구현
- 생육 환경 평가 기능 추가 (점수화)
- 질병 발생 확률 예측 기능 추가
- RAG 기반 AI 분석 통합
