# Copilot / AI Agent Instructions for AiSmartFarm

이 저장소는 React + Vite 기반 SPA 프론트엔드입니다. 아래 지침은 이 코드베이스에서 바로 생산적으로 작업하도록 돕기 위한 구체적이고 검증 가능한 규칙을 제공합니다.

## 빠른 개요 (Big picture)
- **앱 타입:** React (v19) + Vite single-page app. 루트는 `src/`.
- **라우팅:** `src/App.jsx`에서 `react-router-dom`으로 경로를 정의합니다. 주요 경로: `/` (`StartPage`), `/crop` (`CropSelect`).
- **자산:** 이미지·폰트 등은 `src/assets/`에 위치하며 컴포넌트에서 `import`로 사용합니다 (예: `import startBg from "../assets/start.png"`).
- **스타일 방식:** 대부분 컴포넌트 내부의 inline style 객체(`const styles = { ... }`)를 사용합니다. 전역 CSS는 `src/index.css`와 `App.css`에 있습니다.

## 개발·빌드 명령 (명확한 커맨드)
- 로컬 개발 서버 시작: `npm install` 이후 `npm run dev` (Vite, HMR 활성화)
- 프로덕션 빌드: `npm run build` → 산출물은 `dist/` (Vite 기본)
- 빌드 미리보기: `npm run preview`
- 린트: `npm run lint` (프로젝트 루트의 ESLint 규칙 사용)

## 코드 변경시 가이드라인 (구체적 패턴)
- 새 페이지 추가: `src/pages/YourPage.jsx` 생성 → `src/App.jsx`의 `Routes`에 `Route path="/your" element={<YourPage/>}` 추가.
- 자산 추가: `src/assets/`에 파일 추가 후 컴포넌트에서 `import image from "../assets/Name.png"` 방식으로 사용.
- 컴포넌트 스타일: 기존 컴포넌트들(`StartPage.jsx`, `CropSelect.jsx`)을 참고해 inline `styles` 객체 패턴을 따르세요. 전역 규칙을 변경할 때는 `index.css` 또는 `App.css`를 함께 검토.
- 라우터 네비게이션: `useNavigate` 훅을 사용한 내비게이션 패턴을 따릅니다 (예: `const navigate = useNavigate(); navigate('/crop')`).

## 프로젝트 특이사항 및 참고 파일
- `package.json`에는 `dev`, `build`, `preview`, `lint` 스크립트가 있음. (파일: `package.json`)
- 라우팅과 페이지 구성은 `src/App.jsx`와 `src/pages/` 폴더를 확인하세요.
- 사용자 인터랙션과 달력/캘린더 로직은 `src/pages/CropSelect.jsx`에 구현되어 있으니, 날짜·선택 관련 변경은 이 파일을 참고.
- AI/백엔드 연동 시: 저장소 루트의 `AISmartFarm-DiseasePrediction-Response/README.md`에 플랫폼 목표(병해 예측·RAG·LLM 기반)가 적혀 있습니다. 머신러닝·서버 연동 포인트는 해당 서브폴더에서 추가 확인 필요.

## 작업 우선순위와 안전한 변경
- UI 텍스트·문구 변경은 `src/pages/*`에서 직접 수정해도 무방합니다.
- 라우트·데이터 흐름 변경 시, 먼저 `src/App.jsx`와 변경될 페이지들에서 경로·props 전달 방식을 검토하세요.
- 새로운 의존성 추가는 `package.json`에 선언하고 `npm install`을 통해 적절히 테스트하세요. (Vite + React 버전 호환성 확인 권장)

## 체크리스트 예시 (커밋 전)
- `npm run dev`로 기본 페이지가 정상 렌더링되는지 확인
- `npm run lint`로 ESLint 오류가 없는지 확인
- 변경한 컴포넌트에서 자산 경로(대소문자 포함)가 올바른지 확인

## 질문이 필요할 때 (AI 에이전트용)
- 데이터 또는 백엔드 연동 포인트가 불명확하면 `AISmartFarm-DiseasePrediction-Response/README.md`에서 목표를 확인하고, 추가 서버 코드가 있는지 담당자에게 문의하세요.

---
추가로 포함했으면 하는 세부 규칙이나, 특정 파일(예: 테스트, CI 설정 등)을 반영하길 원하시면 알려주세요. 초안을 리포지토리에 적용해도 될까요?
