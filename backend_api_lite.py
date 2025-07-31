from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import uuid
import json
from datetime import datetime
from jose import jwt
import os
from dotenv import load_dotenv

from ai_interviewer_system_lite import InterviewOrchestrator

# 환경 변수 로드
load_dotenv()

app = FastAPI(title="AI 면접관 시스템 (경량화 버전)", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React 앱 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 인증 설정
security = HTTPBearer()
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key-for-development')

# 전역 변수
interview_orchestrator = InterviewOrchestrator()
active_connections: Dict[str, WebSocket] = {}

# 기존 요청/응답 모델
class InterviewStartRequest(BaseModel):
    interview_type: str
    user_profile: Dict

class InterviewResponse(BaseModel):
    session_id: str
    question: str

class UserResponseRequest(BaseModel):
    session_id: str
    response: str

class AnalysisResult(BaseModel):
    session_id: str
    interview_type: str
    duration_minutes: int
    total_exchanges: int
    feedback: str
    scores: Optional[Dict] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# 새로운 모델 - 개인화된 면접
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

class PersonalizedInterviewRequest(BaseModel):
    profile: InterviewProfile

class ProfileSaveRequest(BaseModel):
    profile: InterviewProfile

class ProfileResponse(BaseModel):
    profile_id: str
    status: str
    message: str

# 인증 함수 (선택적)
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# 개발용 간단한 인증 (선택적)
async def optional_auth():
    """개발 환경에서는 인증을 선택적으로 만듦"""
    return "dev_user"

# API 엔드포인트
@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """간단한 로그인 (개발용)"""
    if request.username and request.password:  # 기본적인 검증
        user_id = str(uuid.uuid4())
        token = jwt.encode({"user_id": user_id, "username": request.username}, SECRET_KEY, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer", "user_id": user_id}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# 새로운 API - 프로필 관리
@app.post("/api/interview/profile", response_model=ProfileResponse)
async def save_interview_profile(
    request: ProfileSaveRequest,
    user_id: str = Depends(optional_auth)
):
    """면접 프로필 저장"""
    try:
        profile_id = str(uuid.uuid4())
        profile = request.profile
        profile.id = profile_id
        profile.createdAt = datetime.now()
        
        # 프로필 저장 (메모리에 임시 저장, 실제로는 DB에 저장해야 함)
        interview_orchestrator.save_profile(profile_id, profile)
        
        return ProfileResponse(
            profile_id=profile_id,
            status="success",
            message="프로필이 성공적으로 저장되었습니다."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 저장 실패: {str(e)}")

@app.post("/api/interview/start-personalized", response_model=InterviewResponse)
async def start_personalized_interview(
    request: PersonalizedInterviewRequest,
    user_id: str = Depends(optional_auth)
):
    """개인화된 면접 시작"""
    session_id = str(uuid.uuid4())
    
    try:
        opening_question = await interview_orchestrator.start_personalized_interview(
            session_id=session_id,
            user_id=user_id,
            profile=request.profile
        )
        
        return InterviewResponse(
            session_id=session_id,
            question=opening_question
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"개인화된 면접 시작 실패: {str(e)}")

# 기존 API - 개인화된 면접으로 리다이렉트
@app.post("/api/interview/start", response_model=InterviewResponse)
async def start_interview(
    request: InterviewStartRequest,
    user_id: str = Depends(optional_auth)  # 개발용 간소화
):
    """기본 면접 시작 (개인화된 면접으로 변환)"""
    session_id = str(uuid.uuid4())
    
    try:
        # 기본 프로필 생성 (기존 API 호환성 유지)
        from ai_interviewer_system_lite import InterviewProfile
        
        basic_profile = InterviewProfile(
            type=request.interview_type,
            institution="면접 기관",
            fields=request.user_profile.get("interests", ["일반"]),
            keywords=[],
            additionalStyle="표준 면접 진행",
            uploadedFiles=[]
        )
        
        opening_question = await interview_orchestrator.start_personalized_interview(
            session_id=session_id,
            user_id=user_id,
            profile=basic_profile
        )
        
        return InterviewResponse(
            session_id=session_id,
            question=opening_question
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/respond")
async def respond_to_question(
    request: UserResponseRequest,
    user_id: str = Depends(optional_auth)
):
    """사용자 응답 처리"""
    try:
        next_question = await interview_orchestrator.process_response(
            session_id=request.session_id,
            user_response=request.response
        )
        
        # WebSocket으로 실시간 응답 전송
        if request.session_id in active_connections:
            try:
                await active_connections[request.session_id].send_text(
                    json.dumps({
                        "type": "question",
                        "content": next_question,
                        "timestamp": datetime.now().isoformat()
                    })
                )
            except Exception as ws_error:
                print(f"WebSocket 전송 오류: {ws_error}")
        
        return {"question": next_question}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/end", response_model=AnalysisResult)
async def end_interview(
    session_id: str,
    user_id: str = Depends(optional_auth)
):
    """면접 종료 및 분석"""
    try:
        analysis = await interview_orchestrator.end_interview(session_id)
        
        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])
        
        return AnalysisResult(
            session_id=analysis["session_id"],
            interview_type=analysis["interview_type"],
            duration_minutes=analysis["duration_minutes"],
            total_exchanges=analysis["total_exchanges"],
            feedback=analysis["feedback"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interview/types")
async def get_interview_types():
    """면접 유형 목록 조회"""
    return {
        "interview_types": [
            {
                "id": "gifted_education",
                "name": "영재교육원 면접",
                "description": "창의성과 탐구력 중심의 영재교육원 입학 면접"
            },
            {
                "id": "science_high",
                "name": "과학고 면접", 
                "description": "과학적 사고력과 수학 능력 평가 면접"
            },
            {
                "id": "university",
                "name": "대학 입시 면접",
                "description": "전공 적합성과 학업 계획 중심의 대학 면접"
            }
        ]
    }

# WebSocket 엔드포인트
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    active_connections[session_id] = websocket
    
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "user_response":
                # 사용자 응답 처리
                try:
                    next_question = await interview_orchestrator.process_response(
                        session_id=session_id,
                        user_response=message["content"]
                    )
                    
                    # 다음 질문 전송
                    await websocket.send_text(json.dumps({
                        "type": "ai_question",
                        "content": next_question,
                        "timestamp": datetime.now().isoformat()
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"응답 처리 중 오류가 발생했습니다: {str(e)}"
                    }))
            
            elif message["type"] == "end_interview":
                # 면접 종료 처리
                try:
                    analysis = await interview_orchestrator.end_interview(session_id)
                    await websocket.send_text(json.dumps({
                        "type": "interview_ended",
                        "analysis": analysis
                    }))
                    break
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"면접 종료 중 오류가 발생했습니다: {str(e)}"
                    }))
                
    except WebSocketDisconnect:
        # 연결 해제 시 정리
        if session_id in active_connections:
            del active_connections[session_id]
        print(f"WebSocket 연결 해제: {session_id}")
    except Exception as e:
        print(f"WebSocket 오류: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
    finally:
        # 정리
        if session_id in active_connections:
            del active_connections[session_id]

# 건강 체크 및 정보 엔드포인트
@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-lite",
        "openai_configured": bool(os.getenv('OPENAI_API_KEY'))
    }

@app.get("/")
async def root():
    return {
        "message": "AI 면접관 시스템 (경량화 버전) API 서버가 정상 작동 중입니다.",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/system/status")
async def system_status():
    """시스템 상태 확인"""
    return {
        "active_sessions": len(interview_orchestrator.sessions),
        "active_websockets": len(active_connections),
        "gemini_api_configured": bool(os.getenv('GOOGLE_API_KEY')),
        "openai_api_configured": bool(os.getenv('OPENAI_API_KEY')),  # 호환성 유지
        "environment": os.getenv('DEBUG', 'false')
    }

if __name__ == "__main__":
    import uvicorn
    
    # 환경 변수에서 설정 읽기
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 AI 면접관 서버 (Gemini 1.5 Pro) 시작: http://{host}:{port}")
    print(f"📚 API 문서: http://{host}:{port}/docs")
    print(f"🔧 Gemini API 설정됨: {bool(os.getenv('GOOGLE_API_KEY'))}")
    print(f"🔧 OpenAI API 설정됨: {bool(os.getenv('OPENAI_API_KEY'))} (호환성)")
    
    uvicorn.run(
        "backend_api_lite:app" if __name__ == "__main__" else app,
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    ) 