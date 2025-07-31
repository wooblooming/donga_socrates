# 🎓 Donga Socrates - AI 면접 시스템

동아 소크라테스 프로젝트 - 영재교육원, 과학고, 대학 입시 등 다양한 면접을 위한 AI 기반 모의면접 챗봇 시스템입니다.

🔗 **GitHub Repository**: https://github.com/wooblooming/donga_socrates

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
# 저장소 클론
git clone https://github.com/wooblooming/donga_socrates.git
cd donga_socrates

# Python 환경 설정 (venv 사용 권장)
python -m venv ai_interview_env
source ai_interview_env/bin/activate  # Linux/Mac
# ai_interview_env\Scripts\activate  # Windows

# Python 의존성 설치
pip install -r requirements.txt

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

# Google Cloud (선택사항)
GOOGLE_APPLICATION_CREDENTIALS=google-cloud-key.json

# 기타 API 키들
ANTHROPIC_API_KEY=your_anthropic_api_key  # Claude 사용시
HUGGINGFACE_API_KEY=your_huggingface_api_key  # HuggingFace 사용시

# 서버 설정
PORT=8000
HOST=0.0.0.0
```

### 3. 서버 실행

```bash
# 백엔드 서버 실행 (포트 8000)
python backend_api_lite.py

# 새 터미널에서 프론트엔드 실행 (포트 3000)
cd frontend
npm start
```

### 4. 접속

브라우저에서 `http://localhost:3000`으로 접속하세요.

## 📁 프로젝트 구조

```
donga_socrates/
├── 📄 backend_api_lite.py          # FastAPI 백엔드 서버
├── 📄 ai_interviewer_system_lite.py # AI 면접관 핵심 로직
├── 📄 requirements.txt             # Python 의존성
├── 📄 .env                         # 환경 변수 (Git 제외)
├── 📄 .gitignore                   # Git 제외 파일 목록
├── 📄 README.md                    # 프로젝트 설명서
├── 📄 google-cloud-key.json        # Google Cloud 인증 키 (Git 제외)
│
├── 📁 frontend/                    # React 프론트엔드
│   ├── 📄 package.json            # Node.js 의존성
│   ├── 📄 tsconfig.json           # TypeScript 설정
│   ├── 📄 tailwind.config.js      # Tailwind CSS 설정
│   ├── 📄 postcss.config.js       # PostCSS 설정
│   ├── 📁 src/
│   │   ├── 📄 App.tsx             # 메인 App 컴포넌트
│   │   ├── 📄 index.tsx           # React 진입점
│   │   ├── 📄 index.css           # 글로벌 스타일
│   │   ├── 📁 components/
│   │   │   ├── 📄 InterviewChat.tsx      # 면접 채팅 컴포넌트
│   │   │   └── 📄 InterviewSetupWizard.tsx # 면접 설정 마법사
│   │   └── 📁 store/
│   │       └── 📄 interviewStore.ts      # Zustand 상태 관리
│   ├── 📁 public/
│   │   ├── 📄 index.html          # HTML 템플릿
│   │   └── 📄 manifest.json       # PWA 매니페스트
│   └── 📁 node_modules/           # NPM 패키지 (Git 제외)
│
├── 📁 기사데이터/                   # 동아사이언스 기사 데이터
│   ├── 📄 majors_list.json        # 전공 목록
│   ├── 📄 review_criteria.json    # 면접 평가 기준
│   ├── 📄 merged_기사데이터.xlsx   # 통합 기사 데이터
│   └── 📄 *.xlsx                  # 기타 기사 데이터 파일들
│
├── 📁 ai_interview_env/            # Python 가상환경 (Git 제외)
├── 📁 __pycache__/                 # Python 캐시 (Git 제외)
│
├── 📄 ai_interview_prompts_v2.md   # AI 면접 프롬프트 가이드
└── 📄 prompt_engineering_guide.md  # 프롬프트 엔지니어링 가이드
```

## 🎮 사용 방법

### 1. 회원가입/로그인
- 간단한 사용자명과 비밀번호로 로그인 (현재 x)

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

### 🐍 Backend (`backend_api_lite.py`)
- **FastAPI** 기반 웹 서버
- WebSocket 실시간 통신
- OpenAI API 연동
- CORS 설정으로 프론트엔드 연결

### 🤖 AI System (`ai_interviewer_system_lite.py`) 
- **AI 면접관** 핵심 로직
- 다양한 면접 유형별 프롬프트 관리
- 동아사이언스 기사 데이터 활용
- 개인화된 면접 질문 생성

### ⚛️ Frontend (`frontend/`)
- **React + TypeScript** SPA
- **Zustand** 상태 관리
- **Tailwind CSS** 스타일링
- WebSocket으로 실시간 채팅
- 음성 인식 지원

### 📊 Data (`기사데이터/`)
- 동아사이언스 과학 기사 데이터베이스
- 전공별 분류 및 평가 기준
- JSON/Excel 형태로 구조화된 데이터

## 🚀 배포 (Vercel)

이 프로젝트는 Vercel을 통해 배포 가능하도록 설정되어 있습니다.

### 1. Vercel 배포 설정
```bash
# Vercel CLI 설치
npm i -g vercel

# 프로젝트 배포
vercel --prod
```

### 2. 환경 변수 설정 (Vercel Dashboard)
- `OPENAI_API_KEY`: OpenAI API 키
- `GOOGLE_APPLICATION_CREDENTIALS`: Google Cloud 인증 키 내용 (JSON)
- 기타 필요한 환경 변수들

## 🚨 주의사항

1. **API 키 보안**: OpenAI API 키를 안전하게 관리하세요
2. **음성 인식**: HTTPS 환경에서만 음성 인식이 정상 작동합니다
3. **브라우저 호환성**: Chrome, Firefox, Edge 최신 버전 권장
4. **네트워크**: WebSocket 연결을 위한 방화벽 설정 확인
5. **민감 파일**: `.env`, `google-cloud-key.json`은 Git에 커밋하지 마세요



## 📞 지원 및 문의

- **GitHub Issues**: [https://github.com/wooblooming/donga_socrates/issues](https://github.com/wooblooming/donga_socrates/issues)
- 프로젝트 관련 문의사항이나 버그 리포트를 남겨주세요

## 📄 라이센스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

---
**© 2024 Donga University Socrates Project** 