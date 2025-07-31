import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import google.generativeai as genai
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class UploadedFile(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    content: str
    size: int

class InterviewProfile(BaseModel):
    id: Optional[str] = None
    type: str  # 'gifted_center', 'science_high', 'university', 'other'
    institution: str
    fields: List[str]  # 관심 영역
    keywords: List[str]  # 관심 주제 키워드
    additionalStyle: str  # 추가 요청사항
    uploadedFiles: List[UploadedFile] = []
    difficulty: Optional[str] = None  # 면접 난이도 ('elementary', 'middle', 'high', 'professional', 'public')
    createdAt: Optional[datetime] = None

class InterviewSession(BaseModel):
    session_id: str
    user_id: str
    interview_type: str
    stage: str = "opening"
    conversation_history: List[Dict] = []
    user_profile: Dict = {}
    personalized_profile: Optional[Dict] = None
    gemini_chat: Optional[Any] = None  # Gemini chat session
    created_at: datetime = datetime.now()

class PersonalizedPromptManager:
    """개인화된 프롬프트 관리자 - Gemini 최적화"""
    
    def __init__(self):
        # 난이도별 가이드라인
        self.difficulty_guidelines = {
            "elementary": {
                "level": "초등 수준 (11-13세)",
                "language": "쉽고 이해하기 쉬운 용어 사용",
                "complexity": "기초 개념 중심, 구체적 예시 활용",
                "interaction": "호기심 유발, 격려 중심의 대화",
                "examples": "일상생활 예시, 간단한 실험이나 관찰"
            },
            "middle": {
                "level": "중등 수준 (14-16세)",
                "language": "기본 전문 용어 포함하되 설명과 함께",
                "complexity": "심화 개념 도입, 논리적 연결 고려",
                "interaction": "탐구 정신 자극, 가정 설정 질문",
                "examples": "교과서 수준의 개념, 실험 설계 사고"
            },
            "high": {
                "level": "고등 수준 (17-19세)",
                "language": "전문 용어 적극 활용",
                "complexity": "복합적 사고, 비판적 분석 요구",
                "interaction": "독립적 사고 유도, 창의적 접근 격려",
                "examples": "대학 수준 개념, 연구 방법론적 접근"
            },
            "professional": {
                "level": "실무 수준 (성인)",
                "language": "전문 분야 용어, 업계 표준 언어",
                "complexity": "실무 경험 기반, 문제해결 중심",
                "interaction": "실무 적용성, 전문성 검증",
                "examples": "실제 업무 사례, 프로젝트 경험"
            },
            "public": {
                "level": "공직 수준 (성인)",
                "language": "공공성 중심 용어, 정책적 관점",
                "complexity": "사회적 책임, 공익성 고려",
                "interaction": "공공 가치 확인, 윤리적 판단",
                "examples": "공공정책 사례, 사회문제 해결방안"
            }
        }
        
        self.base_prompts = {
            "gifted_center": {
                "system": """당신은 영재교육원 전문 면접관입니다. 
                
                **역할과 목표:**
                - 학생의 창의성, 탐구력, 문제해결 능력을 평가
                - 친근하면서도 예리한 통찰력으로 면접 진행
                - 학생의 잠재력과 영재적 특성 발견
                
                **면접 진행 방식:**
                1. 이전 답변을 바탕으로 자연스럽게 후속 질문
                2. 답변의 깊이에 따라 추가 탐구 또는 다음 주제로 전환
                3. 긍정적인 피드백과 함께 더 깊은 사고 유도
                4. 창의적 사고를 자극하는 가상의 상황 제시
                
                **평가 기준:**
                - 호기심과 탐구 의지 (왜? 어떻게? 라는 질문을 던지는가?)
                - 창의적 사고력 (기존과 다른 관점으로 접근하는가?)
                - 학습에 대한 열정 (자발적 학습 동기가 있는가?)
                - 문제해결 접근법 (체계적이고 논리적인 사고를 하는가?)
                """,
                "focus_areas": ["창의성", "탐구력", "문제해결능력", "학습동기"]
            },
            
            "science_high": {
                "system": """당신은 과학고 입학 면접관입니다.
                
                **역할과 목표:**
                - 학생의 과학적 사고력, 수학 능력, 연구 열정을 종합 평가
                - 논리적이고 체계적이지만 학생이 편안하게 느끼도록 진행
                - 미래 과학자로서의 잠재력 평가
                
                **면접 진행 방식:**
                1. 학생의 답변에서 과학적 개념이나 원리 찾아 확장 질문
                2. 수학/과학 기초 실력을 자연스럽게 확인
                3. 가설 설정, 실험 설계 등 연구 방법론적 사고 유도
                4. 과학계 이슈나 최신 연구에 대한 관심도 확인
                
                **평가 기준:**
                - 과학적 사고력 (현상을 과학적으로 설명하려 하는가?)
                - 논리적 추론 능력 (체계적이고 일관된 논리 전개를 하는가?)
                - 수학/과학 기초 실력 (기본 개념과 원리를 이해하고 있는가?)
                - 연구자로서의 자질 (호기심, 끈기, 객관성을 가지고 있는가?)
                """,
                "focus_areas": ["과학적사고", "수학능력", "실험설계", "연구자질"]
            },
            
            "university": {
                "system": """당신은 대학교 입학 면접관입니다.
                
                **역할과 목표:**
                - 지원자의 전공 적합성, 학업 계획, 인성을 종합 평가
                - 공정하고 객관적인 시각으로 면접 진행
                - 대학생으로서의 준비도와 성장 가능성 평가
                
                **면접 진행 방식:**
                1. 전공 관련 경험이나 관심사를 바탕으로 깊이 있는 질문
                2. 구체적인 사례와 경험을 요구하여 진정성 확인
                3. 미래 계획의 현실성과 구체성 평가
                4. 사회적 책임감과 리더십 경험 탐구
                
                **평가 기준:**
                - 전공에 대한 이해와 적합성 (왜 이 전공을 선택했는가?)
                - 학업 계획의 구체성 (명확한 목표와 계획이 있는가?)
                - 자기주도적 학습 능력 (스스로 학습하고 성장하는가?)
                - 사회적 책임감 (타인을 배려하고 사회에 기여하려 하는가?)
                """,
                "focus_areas": ["전공적합성", "학업계획", "자기주도성", "사회적책임감"]
            }
        }
    
    def generate_personalized_system_prompt(self, profile: InterviewProfile) -> str:
        """개인화된 시스템 프롬프트 생성"""
        base_prompt = self.base_prompts.get(profile.type, {}).get("system", "")
        
        # 난이도별 가이드라인 추가
        difficulty = profile.difficulty or "high"  # 기본값: 고등 수준
        difficulty_guide = self.difficulty_guidelines.get(difficulty, self.difficulty_guidelines["high"])
        
        # 업로드 파일 정보 요약
        file_info = ""
        if profile.uploadedFiles:
            file_summaries = []
            for file in profile.uploadedFiles:
                content_preview = file.content[:200] + "..." if len(file.content) > 200 else file.content
                file_summaries.append(f"- {file.name}: {content_preview}")
            file_info = f"""
            **업로드된 자료:** 
            {chr(10).join(file_summaries)}
            """
        
        # 키워드 정보를 자연스럽게 처리
        keyword_guidance = ""
        if profile.keywords:
            keyword_list = ', '.join(profile.keywords)
            keyword_guidance = f"""
            
        === 지원자 관심사 참고 (자연스럽게 활용할 것) ===
        지원자가 평소 관심을 보이는 주제들: {keyword_list}
        
        **중요한 키워드 활용 가이드라인:**
        - 키워드를 직접 언급하지 말고, 자연스러운 대화 흐름에서만 활용
        - 지원자의 답변과 연관성이 있을 때만 관련 질문으로 유도
        - "양자역학에 대해 어떻게 생각하세요?" 같은 직접적 언급 금지
        - 대신 "그 분야에서 특히 어떤 부분이 흥미로우신가요?" 같은 자연스러운 질문
        - 모든 키워드를 다룰 필요 없음, 대화 흐름에 맞는 것만 선택적 활용
            """
        
        personalization = f"""
        
        === 개인화 정보 ===
        **지원 기관:** {profile.institution}
        **관심 분야:** {', '.join(profile.fields)}
        **추가 요청사항:** {profile.additionalStyle}
        {file_info}
        {keyword_guidance}
        
        === 난이도별 면접 가이드라인 ===
        **면접 난이도:** {difficulty_guide['level']}
        **언어 사용:** {difficulty_guide['language']}
        **내용 복잡도:** {difficulty_guide['complexity']}
        **상호작용 방식:** {difficulty_guide['interaction']}
        **질문 예시 수준:** {difficulty_guide['examples']}
        
        === 면접 진행 가이드라인 ===
        1. **개인화 반영**: 위 정보를 바탕으로 맞춤형 질문 진행
        2. **난이도 조절**: 위 난이도 설정에 맞춰 질문의 수준과 언어를 조절
        3. **자연스러운 키워드 활용**: 억지로 언급하지 말고 대화 흐름에 맞게만 활용
        4. **멀티턴 대화**: 이전 답변을 기억하고 자연스럽게 이어가기
        5. **적절한 피드백**: "좋은 답변이네요", "흥미롭군요" 등으로 격려
        6. **깊이 있는 탐구**: 표면적 답변에서 더 깊은 사고로 유도
        7. **자연스러운 마무리**: 적절한 시점에서 면접 종료 신호
        
        **중요**: 매번 답변을 듣고 나서 해당 답변에 대한 간단한 피드백을 준 후, 
        설정된 난이도 수준에 맞는 언어와 내용으로 자연스럽게 후속 질문을 이어가세요.
        키워드는 참고사항일 뿐, 무조건 언급할 필요는 없습니다.
        """
        
        return base_prompt + personalization
    
    def generate_opening_question(self, profile: InterviewProfile) -> str:
        """개인화된 오프닝 질문 생성 - 난이도별 조절"""
        institution = profile.institution
        interview_type_kr = {
            "gifted_center": "영재교육원",
            "science_high": "과학고",
            "university": "대학교"
        }.get(profile.type, "교육기관")
        
        # 난이도별 인사말과 질문 스타일 조절
        difficulty = profile.difficulty or "high"
        
        if difficulty == "elementary":
            greeting = f"안녕! {institution} {interview_type_kr} 면접에 와줘서 고마워요. 😊"
            comfort = "긴장하지 말고 평소처럼 편하게 이야기해주면 돼요."
            question = f"먼저 자기소개를 해볼까요? 이름이랑 몇 학년인지, 그리고 {institution}에 왜 관심이 생겼는지 재미있게 들려주세요!"
        elif difficulty == "middle":
            greeting = f"안녕하세요! {institution} {interview_type_kr} 면접에 참여해주셔서 감사합니다."
            comfort = "편안한 마음으로 자신의 생각을 표현해주세요."
            question = f"먼저 자기소개를 해주시겠어요? 이름, 학년, 그리고 {institution}에 지원하게 된 계기를 말씀해주세요."
        else:  # high, professional, public
            greeting = f"안녕하세요! {institution} {interview_type_kr} 면접에 참여해주셔서 감사합니다."
            comfort = "긴장하지 마시고 편안하게 자신을 표현해주세요. 면접관으로서 여러분의 잠재력과 가능성을 발견하는 것이 제 목표입니다."
            question = f"먼저 간단하게 자기소개를 해주시겠어요? 이름, 현재 상황, 그리고 {institution}에 관심을 갖게 된 특별한 계기가 있다면 함께 말씀해주세요."
        
        return f"""{greeting} 

{comfort}

{question}"""

class InterviewOrchestrator:
    """면접 진행 총괄 관리자 - Gemini 1.5 Pro 최적화"""
    
    def __init__(self):
        self.personalized_prompt_manager = PersonalizedPromptManager()
        self.sessions: Dict[str, InterviewSession] = {}
        self.profiles: Dict[str, InterviewProfile] = {}
        
        # Gemini API 초기화
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            print("경고: GOOGLE_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
            return
            
        genai.configure(api_key=google_api_key)
        
        # Gemini 모델 설정
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1000,
            }
        )
        
        print("✅ Gemini 1.5 Pro 모델이 성공적으로 초기화되었습니다.")
    
    def save_profile(self, profile_id: str, profile: InterviewProfile):
        """프로필 저장"""
        self.profiles[profile_id] = profile
        print(f"프로필 저장됨: {profile_id} - {profile.institution}")
    
    def get_profile(self, profile_id: str) -> Optional[InterviewProfile]:
        """프로필 조회"""
        return self.profiles.get(profile_id)
    
    async def start_personalized_interview(self, session_id: str, user_id: str, 
                                         profile: InterviewProfile) -> str:
        """개인화된 면접 시작 - Gemini Chat Session 활용"""
        
        # Gemini Chat Session 시작 (시스템 프롬프트는 나중에 전송)
        chat = self.model.start_chat(history=[])
        
        session = InterviewSession(
            session_id=session_id,
            user_id=user_id,
            interview_type=profile.type,
            personalized_profile=profile.model_dump(),
            gemini_chat=chat
        )
        self.sessions[session_id] = session
        
        # 개인화된 오프닝 질문 생성 (기존 방식 사용)
        opening_question = self.personalized_prompt_manager.generate_opening_question(profile)
        
        # 오프닝 질문을 대화 이력에 추가
        session.conversation_history.append({
            "role": "assistant",
            "content": opening_question,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"✅ 개인화된 면접 시작: {session_id} - {profile.institution}")
        print(f"오프닝 질문: {opening_question[:100]}...")
        return opening_question
    
    async def process_response(self, session_id: str, user_response: str) -> str:
        """사용자 응답 처리 및 다음 질문 생성 - Gemini 멀티턴 대화"""
        session = self.sessions.get(session_id)
        if not session:
            return "❌ 세션을 찾을 수 없습니다. 면접을 다시 시작해주세요."
        
        try:
            # 사용자 응답을 이력에 추가
            session.conversation_history.append({
                "role": "user",
                "content": user_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Gemini Chat Session을 통해 응답 생성
            if not session.gemini_chat:
                return "❌ 면접 세션이 초기화되지 않았습니다. 면접을 다시 시작해주세요."
            
            # 첫 번째 사용자 응답인 경우: 시스템 프롬프트와 함께 대화 시작
            if len(session.conversation_history) == 2:  # 오프닝 질문 + 첫 번째 사용자 응답
                # 개인화된 시스템 프롬프트 생성
                profile = InterviewProfile(**session.personalized_profile)
                system_prompt = self.personalized_prompt_manager.generate_personalized_system_prompt(profile)
                
                # 시스템 프롬프트와 첫 번째 응답을 함께 전송
                gemini_response = session.gemini_chat.send_message(
                    f"[시스템] {system_prompt}\n\n[지원자 첫 번째 답변] {user_response}\n\n위 답변을 바탕으로 자연스러운 후속 질문이나 피드백을 해주세요. 개인화된 정보를 고려하여 면접을 이어가주세요."
                )
            else:
                # 일반적인 후속 응답
                gemini_response = session.gemini_chat.send_message(
                    f"[지원자 답변] {user_response}\n\n위 답변을 바탕으로 자연스러운 후속 질문이나 피드백을 해주세요. 이전 대화 맥락을 고려하여 면접을 이어가주세요."
                )
            
            next_question = gemini_response.text.strip()
            
            # AI 응답을 대화 이력에 추가
            session.conversation_history.append({
                "role": "assistant",
                "content": next_question,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"✅ 면접 대화 진행: {session_id} - {len(session.conversation_history)}번째 교환")
            return next_question
            
        except Exception as e:
            print(f"❌ Gemini API 호출 오류: {e}")
            return self._get_fallback_question(session)
    
    def _get_fallback_question(self, session: InterviewSession) -> str:
        """Gemini API 실패 시 사용할 기본 질문"""
        fallback_questions = [
            "좀 더 구체적인 예시를 들어주실 수 있을까요?",
            "그 경험에서 가장 중요하게 배운 점은 무엇인가요?",
            "앞으로의 계획이나 목표에 대해 말씀해주세요.",
            "마지막으로 하고 싶은 말씀이 있다면 자유롭게 해주세요."
        ]
        
        conversation_count = len([msg for msg in session.conversation_history if msg["role"] == "user"])
        if conversation_count < len(fallback_questions):
            return fallback_questions[conversation_count - 1]
        else:
            return fallback_questions[-1]
    
    async def end_interview(self, session_id: str) -> Dict:
        """면접 종료 및 결과 분석"""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "세션을 찾을 수 없습니다."}
        
        try:
            # Gemini를 활용한 면접 분석 및 피드백 생성
            if session.gemini_chat:
                conversation_summary = self._format_conversation_for_analysis(session.conversation_history)
                
                analysis_prompt = f"""
                다음은 방금 진행된 면접의 전체 대화입니다:
                
                {conversation_summary}
                
                이 면접을 바탕으로 다음 형식으로 분석해주세요:
                
                **면접 분석 결과**
                1. **답변 품질**: 전반적인 답변의 구체성과 성의
                2. **전공 적합성**: 지원 분야에 대한 이해도와 열정
                3. **성장 가능성**: 잠재력과 발전 가능성
                4. **개선 제안**: 향후 면접이나 준비 시 고려사항
                5. **총평**: 한줄 요약
                
                객관적이고 건설적인 피드백을 제공해주세요.
                """
                
                analysis_response = session.gemini_chat.send_message(analysis_prompt)
                ai_feedback = analysis_response.text.strip()
            else:
                ai_feedback = "면접 세션에 문제가 있어 AI 분석을 생성할 수 없습니다."
        
        except Exception as e:
            print(f"AI 피드백 생성 오류: {e}")
            ai_feedback = "AI 피드백 생성 중 오류가 발생했습니다."
        
        # 면접 결과 분석
        analysis = {
            "session_id": session_id,
            "interview_type": session.interview_type,
            "institution": session.personalized_profile.get("institution", "미상") if session.personalized_profile else "미상",
            "duration_minutes": (datetime.now() - session.created_at).seconds // 60,
            "total_exchanges": len([msg for msg in session.conversation_history if msg["role"] == "user"]),
            "conversation_log": session.conversation_history,
            "ai_feedback": ai_feedback,
            "basic_feedback": self._generate_basic_feedback(session)
        }
        
        # 세션 정리
        del self.sessions[session_id]
        print(f"✅ 면접 종료: {session_id}")
        
        return analysis
    
    def _format_conversation_for_analysis(self, conversation_history: List[Dict]) -> str:
        """대화 이력을 분석용으로 포맷팅"""
        formatted_conversation = []
        for msg in conversation_history:
            role = "면접관" if msg["role"] == "assistant" else "지원자"
            content = msg["content"]
            formatted_conversation.append(f"{role}: {content}")
        
        return "\n\n".join(formatted_conversation)
    
    def _generate_basic_feedback(self, session: InterviewSession) -> str:
        """기본 피드백 생성"""
        total_responses = len([msg for msg in session.conversation_history if msg["role"] == "user"])
        
        if total_responses >= 5:
            return "면접에 적극적으로 참여해주셨습니다. 답변이 구체적이고 성의있게 작성되었습니다."
        elif total_responses >= 3:
            return "면접에 참여해주셔서 감사합니다. 더 구체적인 예시와 경험을 공유해주시면 더 좋을 것 같습니다."
        else:
            return "더 구체적이고 상세한 답변을 통해 자신을 어필해보세요."

# 사용 예시 및 테스트 함수
async def test_personalized_interview():
    """개인화된 면접 테스트"""
    orchestrator = InterviewOrchestrator()
    
    # 테스트용 프로필 생성
    test_profile = InterviewProfile(
        type="university",
        institution="서울대학교 공과대학",
        fields=["컴퓨터과학", "인공지능"],
        keywords=["머신러닝", "딥러닝", "프로그래밍"],
        additionalStyle="논리적이고 체계적인 질문을 선호합니다."
    )
    
    # 면접 시작
    session_id = "test_session_001"
    opening = await orchestrator.start_personalized_interview(
        session_id=session_id,
        user_id="user_123",
        profile=test_profile
    )
    
    print(f"🎤 면접관: {opening}")
    
    # 테스트 응답들
    test_responses = [
        "안녕하세요. 저는 김학생입니다. 고등학교 때부터 프로그래밍에 관심이 많았고, 특히 AI 기술로 사회 문제를 해결하고 싶어 서울대 컴공과에 지원했습니다.",
        "고등학교 때 코딩 동아리에서 챗봇을 만들어봤는데, 그 경험이 AI에 대한 관심을 더욱 키웠습니다. 단순한 규칙 기반 챗봇이었지만, 사용자와 상호작용하는 모습이 신기했어요.",
        "대학에서는 머신러닝과 딥러닝을 깊이 공부하고, 실제 문제에 적용해보는 프로젝트를 많이 하고 싶습니다. 특히 의료 분야에 AI를 적용하는 연구에 관심이 있어요."
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"\n👤 지원자: {response}")
        next_question = await orchestrator.process_response(session_id, response)
        print(f"🎤 면접관: {next_question}")
    
    # 면접 종료
    print("\n" + "="*50)
    result = await orchestrator.end_interview(session_id)
    print("📋 면접 분석 결과:")
    print(f"- 총 교환 횟수: {result['total_exchanges']}")
    print(f"- 면접 시간: {result['duration_minutes']}분")
    print(f"- AI 피드백:\n{result['ai_feedback']}")

if __name__ == "__main__":
    print("🚀 AI 면접 시스템 (Gemini 1.5 Pro) 시작...")
    asyncio.run(test_personalized_interview()) 