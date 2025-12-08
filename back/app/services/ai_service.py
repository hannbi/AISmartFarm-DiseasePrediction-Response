import logging
from openai import OpenAI
from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.models.sensor import ProcessedSensorData, AIAnalysisResponse
from app.services.ncpms_service import NcpmsService

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """RAG 기반 AI 분석 서비스 (OpenAI Assistants API + Vector Store)"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            default_headers={"OpenAI-Beta": "assistants=v2"}
        )
        self.model = settings.OPENAI_MODEL
        self.ncpms_service = NcpmsService()
        self.vector_store_id = settings.VECTOR_STORE_ID
        self.assistant_id = settings.ASSISTANT_ID or None
        
    def _create_system_prompt(self, crop_type: str = "default") -> str:
        """시스템 프롬프트 생성"""
        return f"""당신은 스마트팜 생육 환경 분석 및 병해 예측 전문가입니다.
작물 종류: {crop_type}

센서 데이터를 분석하여 다음 정보를 제공해야 합니다:

1. **생육 환경 평가** (0-100점)
   - 현재 환경이 해당 작물의 최적 생육 조건과 얼마나 일치하는지 평가
   - 온도, 습도, 토양습도 각각의 적합도 점수
   - 전체 점수 기준: 90-100(최적), 70-89(양호), 50-69(주의), 0-49(불량)

2. **질병 발생 확률 예측**
   - 현재 환경 조건을 기반으로 발생 가능한 질병들을 확률(%) 순으로 정렬
   - 각 질병의 발생 원인, 증상, 예방법 포함
   - 최소 2-3개 질병 예측 (확률이 10% 이상인 것만)

3. **종합 위험도**: 낮음/중간/높음

4. **구체적인 권장 조치** (3-5개)

5. **최적 환경 조건** (해당 작물 기준)

응답은 **반드시** 다음 JSON 형식으로만 제공해주세요:
{{
  "growth_environment": {{
    "overall_score": 75.5,
    "status": "양호",
    "temperature_score": 85.0,
    "humidity_score": 60.0,
    "soil_moisture_score": 80.0,
    "detail": "상세 평가 내용"
  }},
  "diseases": [
    {{
      "name": "질병명",
      "probability": 68.5,
      "reason": "발생 원인",
      "symptoms": "주요 증상",
      "prevention": "예방 방법"
    }}
  ],
  "risk_level": "중간",
  "recommendations": ["권장사항1", "권장사항2", "권장사항3"],
  "optimal_conditions": {{
    "temperature": "20-25°C",
    "humidity": "50-60%",
    "soil_moisture": "40-50%"
  }},
  "analysis_summary": "종합 분석 요약"
}}

중요: JSON 형식을 정확히 지켜주세요. 질병은 확률이 높은 순서대로 정렬해주세요.
"""
    
    def _create_user_prompt(
        self,
        sensor_data_text: str,
        crop_type: Optional[str] = None,
        user_context: Optional[str] = None
    ) -> str:
        """사용자 프롬프트 생성"""
        prompt = sensor_data_text
        
        if crop_type:
            prompt += f"\n\n작물 종류: {crop_type}"
        
        if user_context:
            prompt += f"\n\n추가 정보: {user_context}"
        
        return prompt
    
    async def analyze_with_rag(
        self,
        processed_data: ProcessedSensorData,
        sensor_data_text: str,
        crop_type: Optional[str] = None,
        user_context: Optional[str] = None
    ) -> AIAnalysisResponse:
        """RAG를 활용한 센서 데이터 분석 (Assistants API + Vector Store)"""
        logger.info(f"Starting AI analysis for device: {processed_data.device_id}, crop: {crop_type}")
        
        try:
            # Vector Store 사용 여부 확인
            if self.vector_store_id:
                # Assistants API 사용 (Vector Store 연동)
                response_content = await self._analyze_with_assistant(
                    sensor_data_text, crop_type, user_context
                )
            else:
                # 일반 Chat Completions API 사용 (fallback)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self._create_system_prompt(crop_type or "default")},
                        {"role": "user", "content": self._create_user_prompt(
                            sensor_data_text, crop_type, user_context
                        )}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                response_content = response.choices[0].message.content
            
            # 응답 파싱
            ai_response = response_content
            logger.info("AI analysis completed successfully")
            
            # JSON 파싱 시도 (실제로는 더 robust한 파싱 필요)
            import json
            try:
                # JSON 블록 추출
                if "```json" in ai_response:
                    json_str = ai_response.split("```json")[1].split("```")[0].strip()
                elif "```" in ai_response:
                    json_str = ai_response.split("```")[1].split("```")[0].strip()
                else:
                    json_str = ai_response
                
                parsed_response = json.loads(json_str)
                # 응답 구조 검증 및 생성
                from app.models.sensor import GrowthEnvironmentScore, DiseaseInfo
                
                growth_env = parsed_response.get("growth_environment", {})
                diseases_data = parsed_response.get("diseases", [])
                
                # NCPMS API로 병해충 정보 보강
                enriched_diseases = await self._enrich_diseases_with_ncpms(
                    diseases_data, 
                    crop_type
                )
                
                return AIAnalysisResponse(
                    growth_environment=GrowthEnvironmentScore(
                        overall_score=growth_env.get("overall_score", 70.0),
                        status=growth_env.get("status", "양호"),
                        temperature_score=growth_env.get("temperature_score", 70.0),
                        humidity_score=growth_env.get("humidity_score", 70.0),
                        soil_moisture_score=growth_env.get("soil_moisture_score"),
                        detail=growth_env.get("detail", "분석 중입니다.")
                    ),
                    diseases=enriched_diseases,
                    risk_level=parsed_response.get("risk_level", "중간"),
                    recommendations=parsed_response.get("recommendations", ["데이터를 계속 모니터링하세요"]),
                    optimal_conditions=parsed_response.get("optimal_conditions", {}),
                    analysis_summary=parsed_response.get("analysis_summary", "분석이 완료되었습니다."),
                    timestamp=datetime.now()
                )
                
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 응답
                logger.warning("Failed to parse JSON response, using fallback")
                return self._create_fallback_response(processed_data, ai_response)
        
        except Exception as e:
            logger.error(f"Error during AI analysis: {str(e)}")
            raise
    
    def _create_fallback_response(
        self,
        processed_data: ProcessedSensorData,
        ai_text: str
    ) -> AIAnalysisResponse:
        """파싱 실패 시 기본 응답 생성"""
        from app.models.sensor import GrowthEnvironmentScore, DiseaseInfo
        
        # 상태에 따른 기본 위험도 및 점수 설정
        risk_level = "낮음"
        overall_score = 80.0
        status = "양호"
        
        if processed_data.overall_status == "위험":
            risk_level = "높음"
            overall_score = 40.0
            status = "불량"
        elif processed_data.overall_status == "경고":
            risk_level = "중간"
            overall_score = 65.0
            status = "주의"
        
        # 기본 권장사항
        recommendations = []
        if processed_data.temperature_status == "위험":
            recommendations.append("온도 조절이 필요합니다.")
        if processed_data.humidity_status == "위험":
            recommendations.append("습도 조절이 필요합니다.")
        if not recommendations:
            recommendations.append("현재 환경을 유지하세요.")
        
        # 기본 질병 정보
        diseases = [
            DiseaseInfo(
                name="일반 병해",
                probability=30.0,
                reason="환경 조건 분석 필요",
                symptoms="정기적인 모니터링 필요",
                prevention="최적 환경 유지"
            )
        ]
        
        return AIAnalysisResponse(
            growth_environment=GrowthEnvironmentScore(
                overall_score=overall_score,
                status=status,
                temperature_score=70.0,
                humidity_score=70.0,
                soil_moisture_score=70.0,
                detail="센서 데이터를 기반으로 한 기본 평가입니다."
            ),
            diseases=diseases,
            risk_level=risk_level,
            recommendations=recommendations,
            optimal_conditions={
                "temperature": "20-25°C",
                "humidity": "50-70%",
                "soil_moisture": "40-60%"
            },
            analysis_summary=ai_text[:200] if len(ai_text) > 200 else ai_text,
            timestamp=datetime.now()
        )
    
    async def _enrich_diseases_with_ncpms(
        self,
        diseases_data: list,
        crop_type: Optional[str] = None
    ) -> list:
        """
        LLM 분석 결과를 NCPMS 데이터로 보강
        
        Args:
            diseases_data: LLM에서 받은 질병 데이터 리스트
            crop_type: 작물 종류
            
        Returns:
            NCPMS 데이터가 보강된 DiseaseInfo 리스트
        """
        from app.models.sensor import DiseaseInfo
        
        enriched_diseases = []
        
        for disease_dict in diseases_data:
            disease_name = disease_dict.get("name", "미확인")
            
            # NCPMS API로 추가 정보 조회
            ncpms_data = await self.ncpms_service.enrich_disease_info(
                disease_name,
                crop_type
            )
            
            # LLM 데이터와 NCPMS 데이터 통합
            disease_info = DiseaseInfo(
                name=disease_name,
                probability=disease_dict.get("probability", 0.0),
                reason=disease_dict.get("reason", ""),
                symptoms=disease_dict.get("symptoms"),
                prevention=disease_dict.get("prevention"),
                # NCPMS 추가 정보
                scientific_name=ncpms_data.get("scientific_name"),
                images=ncpms_data.get("images", []),
                detailed_symptoms=ncpms_data.get("symptoms"),
                management=ncpms_data.get("management"),
                reference_url=ncpms_data.get("reference_url"),
                source=ncpms_data.get("source", "LLM Analysis")
            )
            
            enriched_diseases.append(disease_info)
            logger.info(f"Enriched disease info for: {disease_name}")
        
        return enriched_diseases
    
    async def _analyze_with_assistant(
        self,
        sensor_data_text: str,
        crop_type: Optional[str] = None,
        user_context: Optional[str] = None
    ) -> str:
        """
        OpenAI Assistants API와 Vector Store를 사용한 RAG 분석
        
        Args:
            sensor_data_text: 센서 데이터 텍스트
            crop_type: 작물 종류
            user_context: 사용자 컨텍스트
            
        Returns:
            AI 분석 결과 텍스트
        """
        import time
        
        logger.info(f"Using Assistants API with Vector Store: {self.vector_store_id}")
        
        # Assistant가 없으면 생성
        if not self.assistant_id:
            logger.info("Creating new assistant with vector store")
            assistant = self.client.beta.assistants.create(
                name="Smart Farm Disease Prediction Expert",
                instructions=self._create_system_prompt(crop_type or "default"),
                model=self.model,
                tools=[{"type": "file_search"}],
                tool_resources={
                    "file_search": {
                        "vector_store_ids": [self.vector_store_id]
                    }
                }
            )
            self.assistant_id = assistant.id
            logger.info(f"Created assistant: {self.assistant_id}")
        
        # Thread 생성
        thread = self.client.beta.threads.create()
        
        # 메시지 추가
        message_content = self._create_user_prompt(
            sensor_data_text, crop_type, user_context
        )
        
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message_content
        )
        
        # Run 실행
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id
        )
        
        # Run 완료 대기
        max_wait_time = 60  # 최대 60초 대기
        start_time = time.time()
        
        while run.status != "completed":
            if time.time() - start_time > max_wait_time:
                logger.error("Assistant API timeout")
                raise TimeoutError("Assistant API timeout after 60 seconds")
            
            if run.status == "failed":
                logger.error(f"Assistant run failed: {run.last_error}")
                raise Exception(f"Assistant run failed: {run.last_error}")
            
            time.sleep(1)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
        
        # 응답 가져오기
        messages = self.client.beta.threads.messages.list(
            thread_id=thread.id
        )
        
        # 가장 최근 assistant 메시지 찾기
        for message in messages.data:
            if message.role == "assistant":
                response_content = message.content[0].text.value
                logger.info("Successfully retrieved response from Assistant API")
                return response_content
        
        raise Exception("No assistant response found")
