# Docker 환경 설정 가이드

AI Smart Farm Backend Docker 환경 구성 및 실행 가이드

## 📋 목차

- [개발 환경 (Development)](#개발-환경-development)
- [프로덕션 환경 (Production)](#프로덕션-환경-production)
- [Docker 명령어 모음](#docker-명령어-모음)
- [문제 해결](#문제-해결)

---

## 🛠️ 개발 환경 (Development)

개발 시 코드 변경사항이 자동으로 반영되는 환경입니다.

### 사전 요구사항

- Docker 설치 (20.10 이상)
- Docker Compose 설치 (v2 이상)

### 1. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성합니다.

```powershell
Copy-Item .env.example .env
```

`.env` 파일을 열어 필요한 값을 입력합니다:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 2. Docker 이미지 빌드

```powershell
docker-compose build
```

### 3. 컨테이너 실행

```powershell
# 백그라운드 실행
docker-compose up -d

# 로그 확인하며 실행
docker-compose up
```

### 4. 서비스 확인

- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/api/health

### 5. 로그 확인

```powershell
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
```

### 6. 컨테이너 중지

```powershell
# 중지
docker-compose stop

# 중지 및 삭제
docker-compose down

# 볼륨까지 삭제
docker-compose down -v
```

---

## 🚀 프로덕션 환경 (Production)

프로덕션 환경은 최적화된 이미지와 Gunicorn을 사용합니다.

### 1. 프로덕션 환경 변수 설정

`.env` 파일에 프로덕션 설정을 추가합니다:

```env
# OpenAI
OPENAI_API_KEY=your_production_api_key
OPENAI_MODEL=gpt-4

# Server
DEBUG=False
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. Nginx 설정 (선택사항)

Nginx를 리버스 프록시로 사용할 경우, 설정 파일을 생성합니다:

```powershell
mkdir nginx
```

`nginx/nginx.conf` 파일 생성:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 3. 프로덕션 빌드 및 실행

```powershell
# 프로덕션 이미지 빌드
docker-compose -f docker-compose.prod.yml build

# 프로덕션 환경 실행
docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. 프로덕션 환경 중지

```powershell
docker-compose -f docker-compose.prod.yml down
```

---

## 📝 Docker 명령어 모음

### 기본 명령어

```powershell
# 컨테이너 목록 확인
docker ps

# 모든 컨테이너 확인 (중지된 것 포함)
docker ps -a

# 이미지 목록 확인
docker images

# 특정 컨테이너 로그 확인
docker logs smartfarm-backend

# 실시간 로그 확인
docker logs -f smartfarm-backend

# 컨테이너 내부 접속
docker exec -it smartfarm-backend bash

# 컨테이너 재시작
docker restart smartfarm-backend
```

### Docker Compose 명령어

```powershell
# 서비스 상태 확인
docker-compose ps

# 특정 서비스만 시작
docker-compose up -d backend

# 특정 서비스 재시작
docker-compose restart backend

# 서비스 스케일링 (워커 증가)
docker-compose up -d --scale backend=3

# 리소스 사용량 확인
docker-compose stats

# 설정 파일 검증
docker-compose config
```

### 정리 명령어

```powershell
# 중지된 컨테이너 삭제
docker container prune

# 사용하지 않는 이미지 삭제
docker image prune

# 사용하지 않는 볼륨 삭제
docker volume prune

# 모든 미사용 리소스 삭제 (주의!)
docker system prune -a
```

---

## 🔍 문제 해결

### 1. 포트 충돌

**문제:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**해결:**
```powershell
# 포트 사용 중인 프로세스 확인
netstat -ano | findstr :8000

# 프로세스 종료 (PID 확인 후)
taskkill /PID <PID> /F

# 또는 docker-compose.yml에서 다른 포트로 변경
ports:
  - "8001:8000"
```

### 2. 이미지 빌드 실패

**문제:** 의존성 설치 중 에러 발생

**해결:**
```powershell
# 캐시 없이 재빌드
docker-compose build --no-cache

# 특정 서비스만 재빌드
docker-compose build --no-cache backend
```

### 3. 환경 변수 적용 안됨

**문제:** `.env` 파일의 변수가 적용되지 않음

**해결:**
```powershell
# 컨테이너 재생성
docker-compose down
docker-compose up -d

# 환경 변수 확인
docker exec smartfarm-backend env | grep OPENAI
```

### 4. 볼륨 마운트 문제 (Windows)

**문제:** 볼륨 마운트가 작동하지 않음

**해결:**
1. Docker Desktop 설정에서 파일 공유 확인
2. WSL2 사용 권장
3. 절대 경로 사용:

```yaml
volumes:
  - C:/Users/Seondo/Documents/GitHub/AISmartFarm-DiseasePrediction-Response/back:/app
```

### 5. 컨테이너가 계속 재시작됨

**문제:** 컨테이너가 시작 후 바로 종료됨

**해결:**
```powershell
# 로그 확인
docker logs smartfarm-backend

# 에러 메시지 확인 후 수정
# 주로 환경 변수 누락이나 포트 충돌 문제
```

---

## 🔐 보안 권장사항

### 개발 환경

1. `.env` 파일을 **절대** Git에 커밋하지 마세요
2. 기본 포트를 변경하여 사용하세요
3. 개발용 API 키를 별도로 사용하세요

### 프로덕션 환경

1. OpenAI API 키를 안전하게 관리하세요
2. HTTPS 사용 (Let's Encrypt 권장)
3. 정기적인 이미지 업데이트
4. 로그 모니터링 설정
5. CORS 오리진을 특정 도메인으로 제한

```powershell
# 프로덕션 환경에서 민감한 정보는 Docker Secrets 사용 (선택사항)
docker secret create openai_key openai_key.txt
```

---

## 📊 모니터링

### 리소스 사용량 확인

```powershell
# 실시간 리소스 모니터링
docker stats smartfarm-backend

# 모든 컨테이너 모니터링
docker-compose stats
```

### 헬스체크 확인

```powershell
# 컨테이너 헬스 상태 확인
docker inspect --format='{{.State.Health.Status}}' smartfarm-backend

# 상세 헬스체크 로그
docker inspect smartfarm-backend | Select-String -Pattern "Health"
```

---

## 🚀 CI/CD 통합 예시

### GitHub Actions (참고)

```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker build -t smartfarm-backend:latest -f Dockerfile.prod .
      
      - name: Run tests
        run: docker run smartfarm-backend:latest pytest
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push smartfarm-backend:latest
```

---

## 📞 추가 도움말

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [FastAPI Docker 가이드](https://fastapi.tiangolo.com/deployment/docker/)

---

**마지막 업데이트:** 2025-12-07
