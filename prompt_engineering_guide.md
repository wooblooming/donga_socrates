# AI 면접관 프롬프트 엔지니어링 가이드

## 🎯 프롬프트 설계 원칙

### 1. 계층적 프롬프트 아키텍처

```
System Level (역할 정의)
    ↓
Context Level (면접 상황)
    ↓
Task Level (구체적 임무)
    ↓
Format Level (출력 형식)
```

### 2. 핵심 설계 요소

#### A. 페르소나 설정 (Persona Design)
```python
INTERVIEWER_PERSONAS = {
    "gifted_education": {
        "role": "영재교육원 전문 면접관",
        "personality": "친근하면서도 예리한 통찰력을 가진",
        "expertise": ["창의성 평가", "문제해결력 측정", "탐구력 확인"],
        "communication_style": "학생 수준에 맞는 친근한 대화",
        "evaluation_focus": ["호기심", "창의적 사고", "학습 의욕"]
    },
    
    "science_high": {
        "role": "과학고 입학 면접관",
        "personality": "논리적이고 체계적인",
        "expertise": ["과학적 사고력", "수학 능력", "연구 잠재력"],
        "communication_style": "학술적이지만 격려하는",
        "evaluation_focus": ["논리적 사고", "과학적 호기심", "실험 설계 능력"]
    }
}
```

#### B. 동적 프롬프트 생성 전략

```python
def generate_adaptive_prompt(session_context):
    """
    면접 진행 상황에 따른 적응형 프롬프트 생성
    """
    base_template = """
    당신은 {interviewer_role}입니다.
    
    현재 상황:
    - 면접 단계: {current_stage}
    - 지원자 수준: {candidate_level}
    - 이전 답변 품질: {response_quality}
    - 대화 진행도: {progress_ratio}
    
    평가 기준:
    {evaluation_criteria}
    
    다음 질문 생성 지침:
    1. 지원자의 답변 수준을 고려하여 {difficulty_adjustment}
    2. {focus_area}에 대한 심화 탐구
    3. {question_type} 형태의 질문으로 구성
    4. 면접 분위기는 {atmosphere} 유지
    
    제약사항:
    - 질문 길이: {max_length}자 이내
    - 언어 수준: {language_level}
    - 금지 주제: {forbidden_topics}
    """
    
    return base_template.format(**session_context)
```

### 3. 면접 단계별 프롬프트 전략

#### Phase 1: 아이스브레이킹 (Ice Breaking)
```python
ICEBREAKING_PROMPTS = {
    "system": """
    면접의 첫 단계입니다. 지원자의 긴장을 완화하고 
    자연스러운 대화 분위기를 조성해야 합니다.
    
    목표:
    - 지원자의 기본 정보 파악
    - 긴장감 해소
    - 대화 스타일 파악
    """,
    
    "guidelines": [
        "친근하고 따뜻한 어조 사용",
        "간단한 자기소개부터 시작",
        "지원자의 관심사 파악",
        "부담 없는 질문으로 시작"
    ]
}
```

#### Phase 2: 핵심 평가 (Core Assessment)
```python
CORE_ASSESSMENT_PROMPTS = {
    "system": """
    면접의 핵심 단계입니다. 지원자의 역량을 체계적으로 평가해야 합니다.
    
    평가 영역별 질문 전략:
    - 창의성: 가상 시나리오 문제 제시
    - 논리력: 단계적 사고 과정 확인
    - 전문성: 관심 분야 심화 질문
    - 인성: 가치관 및 태도 탐색
    """,
    
    "question_patterns": {
        "scenario_based": "만약 ~라면 어떻게 하시겠습니까?",
        "experience_based": "~한 경험이 있다면 말씀해주세요",
        "opinion_based": "~에 대해 어떻게 생각하시나요?",
        "problem_solving": "다음 문제를 어떻게 해결하시겠습니까?"
    }
}
```

#### Phase 3: 심화 탐구 (Deep Dive)
```python
DEEP_DIVE_PROMPTS = {
    "system": """
    지원자의 답변을 바탕으로 심화 질문을 진행합니다.
    
    전략:
    - 이전 답변의 핵심 포인트 심화
    - 구체적인 예시와 근거 요구
    - 다각도 관점에서 접근
    - 지원자의 사고 깊이 측정
    """,
    
    "follow_up_patterns": [
        "방금 말씀하신 {키워드}에 대해 좀 더 구체적으로 설명해주시겠어요?",
        "그렇게 생각하시는 특별한 이유가 있나요?",
        "다른 방법으로는 어떻게 접근할 수 있을까요?",
        "실제로 그런 상황이 발생한다면 어떤 어려움이 있을까요?"
    ]
}
```

## 🔄 실시간 프롬프트 최적화

### 1. 답변 품질 기반 적응
```python
def adjust_difficulty_based_on_response(response_analysis):
    """
    지원자의 답변 수준에 따른 난이도 조절
    """
    difficulty_levels = {
        "excellent": {
            "next_question_complexity": "high",
            "follow_up_depth": "advanced",
            "challenge_level": "increased"
        },
        "good": {
            "next_question_complexity": "medium",
            "follow_up_depth": "moderate", 
            "challenge_level": "maintained"
        },
        "basic": {
            "next_question_complexity": "low",
            "follow_up_depth": "supportive",
            "challenge_level": "reduced"
        }
    }
    
    return difficulty_levels.get(response_analysis.quality_level)
```

### 2. 대화 흐름 관리
```python
CONVERSATION_FLOW_PROMPTS = {
    "transition_smooth": "그렇군요. 그럼 이번에는 다른 주제로 넘어가볼까요?",
    "transition_connecting": "방금 말씀하신 내용과 연관해서 질문드리겠습니다.",
    "encouragement": "좋은 답변이었습니다. 계속해서 이야기해보세요.",
    "clarification": "혹시 제가 이해한 것이 맞는지 확인해보겠습니다.",
    "time_management": "시간 관계상 다음 질문으로 넘어가겠습니다."
}
```

## 📊 평가 기준 통합 프롬프트

### 1. 실시간 평가 프롬프트
```python
EVALUATION_PROMPT_TEMPLATE = """
지원자의 답변을 다음 기준으로 평가하세요:

답변 내용: "{user_response}"

평가 기준:
1. 내용의 정확성 (1-5점)
2. 논리적 구성 (1-5점) 
3. 창의성 (1-5점)
4. 의사소통 능력 (1-5점)
5. 면접 적합성 (1-5점)

각 항목별 점수와 간단한 근거를 제시하고,
다음 질문 방향을 제안해주세요.

출력 형식:
- 평가점수: {{항목: 점수, 근거}}
- 강점: [강점 요소들]
- 개선점: [개선 필요 요소들]  
- 다음질문방향: [추천 질문 유형]
"""
```

### 2. 종합 피드백 생성
```python
COMPREHENSIVE_FEEDBACK_PROMPT = """
전체 면접 세션을 분석하여 종합 피드백을 생성하세요.

면접 데이터:
- 총 질문 수: {total_questions}
- 평균 답변 길이: {avg_response_length}
- 주요 토픽: {main_topics}
- 답변 품질 추이: {quality_trend}

피드백 구성:
1. 전반적 면접 성과 (A-F 등급)
2. 세부 영역별 점수
3. 주요 강점 3가지
4. 개선 필요 영역 3가지
5. 구체적 개선 방안
6. 추천 학습 리소스

톤: 격려하면서도 건설적인 피드백
길이: 500-800자
"""
```

## 🎛️ 프롬프트 A/B 테스팅 전략

### 1. 질문 유형별 효과성 측정
```python
PROMPT_VARIANTS = {
    "opening_question": {
        "variant_a": "자기소개를 간단히 해주세요.",
        "variant_b": "어떤 계기로 이 분야에 관심을 갖게 되었나요?",
        "variant_c": "오늘 면접에 참여하게 된 소감을 말씀해주세요."
    },
    
    "follow_up_style": {
        "supportive": "정말 좋은 답변이네요. 조금 더 자세히 설명해주시겠어요?",
        "challenging": "흥미로운 관점이군요. 반대 의견도 있을 텐데 어떻게 생각하시나요?",
        "neutral": "이해했습니다. 다른 방법으로는 어떻게 접근하시겠어요?"
    }
}
```

### 2. 성과 지표 추적
```python
PERFORMANCE_METRICS = {
    "engagement": "지원자의 참여도 (답변 길이, 적극성)",
    "satisfaction": "면접 만족도 (후기 평가)",
    "accuracy": "평가의 정확성 (전문가 검토)",
    "efficiency": "면접 진행 효율성 (시간, 질문 수)",
    "diversity": "질문의 다양성 (토픽 커버리지)"
}
```

## 🚀 구현 실행 단계

### 1단계: 기본 프롬프트 구축
- [ ] 면접 유형별 기본 템플릿 작성
- [ ] 페르소나 및 역할 정의
- [ ] 질문 패턴 라이브러리 구축

### 2단계: 동적 생성 시스템
- [ ] 컨텍스트 기반 프롬프트 생성기 개발
- [ ] 답변 분석 및 적응 로직 구현
- [ ] 대화 흐름 관리 시스템 구축

### 3단계: 최적화 및 검증
- [ ] A/B 테스팅 플랫폼 구축
- [ ] 성과 지표 모니터링 시스템
- [ ] 지속적 개선 파이프라인 구축

### 4단계: 고도화
- [ ] 다중 면접관 시뮬레이션
- [ ] 개인화된 면접 시나리오
- [ ] 실시간 감정 분석 연동

이러한 체계적인 프롬프트 엔지니어링을 통해 각 면접 유형에 최적화된 AI 면접관을 구축할 수 있습니다. 