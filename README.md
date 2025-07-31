# AI 면접관 시스템

영재교육원, 과학고, 대학 입시 등 다양한 면접을 위한 AI 기반 모의면접 챗봇 시스템입니다.

## 🎯 주요 기능

- **다양한 면접 유형 지원**: 영재교육원, 과학고, 대학 입시 면접
- **실시간 대화**: WebSocket 기반 실시간 AI 면접관과의 대화
- **음성 인식**: 브라우저 음성 인식을 통한 답변 입력
- **면접 분석**: AI 기반 면접 성과 분석 및 피드백
- **대화 기록**: 전체 면접 과정 저장 및 복기 가능

## 🏗️ 시스템 아키텍처

```
Frontend (React)     Backend (FastAPI)     AI Services
     │                       │                   │
     ├─ React Components     ├─ API Routes       ├─ OpenAI GPT-4
     ├─ WebSocket Client     ├─ WebSocket        ├─ RAG System
     ├─ State Management     ├─ Orchestrator     ├─ Vector DB
     └─ Speech Recognition  └─ Authentication   └─ Prompt Management
```

## 📋 기술 스택

### 백엔드
- **FastAPI**: 웹 API 프레임워크
- **WebSocket**: 실시간 통신
- **OpenAI API**: GPT-4 기반 AI 면접관
- **Pinecone/Chroma**: 벡터 데이터베이스 (RAG)
- **PostgreSQL**: 메인 데이터베이스
- **Redis**: 세션 관리

### 프론트엔드
- **React + TypeScript**: UI 프레임워크
- **Tailwind CSS**: 스타일링
- **Zustand**: 상태 관리
- **Framer Motion**: 애니메이션
- **Speech Recognition**: 음성 인식

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# Python 환경 설정
cd /home/wooble/donga_socrates
source ai_interview_env/bin/activate

# 의존성 설치
pip install -r requirements_minimal.txt

# Node.js 의존성 설치
cd frontend
npm install
cd ..
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/ai_interview

# Redis
REDIS_URL=redis://localhost:6379

# JWT Secret
SECRET_KEY=your_secret_key_here

# Vector DB (선택사항)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
```

### 3. 데이터베이스 설정

```bash
# PostgreSQL 데이터베이스 생성
createdb ai_interview

# Redis 서버 시작
redis-server
```

### 4. 서버 실행

```bash
# 백엔드 서버 실행 (포트 8000)
python backend_api.py

# 새 터미널에서 프론트엔드 실행 (포트 3000)
cd frontend
npm start
```

### 5. 접속

브라우저에서 `http://localhost:3000`으로 접속하세요.

## 📁 프로젝트 구조

```
ai-interviewer/
├── backend_api.py              # FastAPI 백엔드 서버
├── ai_interviewer_system.py    # AI 면접관 핵심 로직
├── requirements.txt            # Python 의존성
├── .env                        # 환경 변수
├── README.md                   # 프로젝트 설명
│
├── frontend/                   # React 프론트엔드
│   ├── package.json           # Node.js 의존성
│   ├── src/
│   │   ├── components/
│   │   │   └── InterviewChat.tsx  # 면접 채팅 컴포넌트
│   │   ├── store/
│   │   │   └── interviewStore.ts  # 상태 관리
│   │   ├── pages/
│   │   ├── utils/
│   │   └── App.tsx
│   └── public/
│
├── database/                   # 데이터베이스 설정
├── tests/                      # 테스트 코드
└── docs/                       # 문서
```

## 🎮 사용 방법

### 1. 회원가입/로그인
- 간단한 사용자명과 비밀번호로 로그인

### 2. 면접 유형 선택
- 영재교육원 면접
- 과학고 면접  
- 대학 입시 면접
- 기타 면접 유형

### 3. 사용자 프로필 설정
- 학년, 관심 분야, 지원 학교 등 입력

### 4. 면접 진행
- AI 면접관의 질문에 텍스트 또는 음성으로 답변
- 실시간 피드백 및 후속 질문

### 5. 결과 분석
- 면접 종료 후 성과 분석 리포트 확인
- 개선점 및 추천사항 제공

## 🔧 주요 컴포넌트 설명

### InterviewOrchestrator
면접 전체 흐름을 관리하는 핵심 클래스
- 세션 관리
- 프롬프트 생성
- LLM API 호출
- RAG 시스템 연동

### PromptManager  
면접 유형별 프롬프트 템플릿 관리
- 계층적 프롬프트 구조
- 동적 프롬프트 생성
- 면접 단계별 질문 관리

### RAGSystem
면접 관련 지식 검색 및 제공
- 벡터 DB 연동
- 면접 유형별 전문 지식
- 컨텍스트 기반 정보 검색

## 🚨 주의사항

1. **API 키 보안**: OpenAI API 키를 안전하게 관리하세요
2. **음성 인식**: HTTPS 환경에서만 음성 인식이 정상 작동합니다
3. **브라우저 호환성**: Chrome, Firefox, Edge 최신 버전 권장
4. **네트워크**: WebSocket 연결을 위한 방화벽 설정 확인

## 🔮 향후 개발 계획

- [ ] 영상 면접 기능 (카메라 연동)
- [ ] 면접 녹화 및 재생 기능
- [ ] 다국어 지원 (영어 면접)
- [ ] 고급 분석 기능 (감정 분석, 발화 속도 등)
- [ ] 면접관 성격 커스터마이징
- [ ] 집단 면접 시뮬레이션
- [ ] 모바일 앱 개발

## 📞 지원 및 문의

프로젝트 관련 문의사항이나 버그 리포트는 GitHub Issues를 이용해주세요.

## 📄 라이센스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다. 