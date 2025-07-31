import React, { useState, useEffect, useRef } from 'react';
import { useInterviewStore } from '../store/interviewStore';
import axios from 'axios';

interface InterviewChatProps {
  sessionId: string | null;
  onInterviewEnd: (analysis: any) => void;
  profile?: any; // 설정한 프로필 정보
}

const InterviewChat: React.FC<InterviewChatProps> = ({ sessionId, onInterviewEnd, profile }) => {
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [actualSessionId, setActualSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasStartedRef = useRef(false); // 면접 시작 여부 추적
  
  const { messages, addMessage } = useInterviewStore();

  // 스크롤을 최하단으로
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 면접 시작 - React StrictMode 중복 실행 방지
  useEffect(() => {
    let isCanceled = false;
    
    // 새로운 sessionId가 오면 hasStartedRef 리셋
    if (sessionId) {
      hasStartedRef.current = false;
    }
    
    if (!hasStartedRef.current && !interviewStarted && profile && sessionId && !actualSessionId) {
      console.log('면접 시작 useEffect 실행:', { 
        hasStarted: hasStartedRef.current, 
        interviewStarted, 
        profile: !!profile, 
        sessionId, 
        actualSessionId 
      });
      
      hasStartedRef.current = true; // 실행 플래그 설정
      
      // 비동기 함수를 즉시 실행하되, cancel 상태 확인
      const startInterview = async () => {
        if (!isCanceled) {
          await startPersonalizedInterview();
        }
      };
      
      startInterview();
    }
    
    // cleanup function: 컴포넌트가 언마운트되거나 effect가 재실행되기 전에 호출
    return () => {
      isCanceled = true;
    };
  }, [sessionId]); // sessionId가 변경될 때만 실행

  // 개인화된 면접 시작
  const startPersonalizedInterview = async () => {
    // 중복 호출 방지
    if (isLoading || interviewStarted || actualSessionId) {
      console.log('중복 호출 방지:', { isLoading, interviewStarted, actualSessionId });
      return;
    }
    
    try {
      setIsLoading(true);
      
      console.log('면접 시작 요청:', profile);
      
      const response = await axios.post('http://localhost:8000/api/interview/start-personalized', {
        profile: profile
      });

      console.log('면접 시작 응답:', response.data);

      const newSessionId = response.data.session_id;
      const welcomeMessage = response.data.question || 
        `안녕하세요! ${profile?.institution || '지원 기관'} 면접에 오신 것을 환영합니다. 자기소개를 부탁드립니다.`;

      setActualSessionId(newSessionId);

      addMessage({
        role: 'assistant',
        content: welcomeMessage,
        timestamp: new Date().toISOString()
      });

      setCurrentQuestion(welcomeMessage);
      setInterviewStarted(true);
    } catch (error) {
      console.error('면접 시작 실패:', error);
      // 기본 환영 메시지
      const defaultMessage = `안녕하세요! ${profile?.institution || '지원 기관'} 면접에 오신 것을 환영합니다. 자기소개를 부탁드립니다.`;
      addMessage({
        role: 'assistant',
        content: defaultMessage,
        timestamp: new Date().toISOString()
      });
      setCurrentQuestion(defaultMessage);
      setInterviewStarted(true);
    } finally {
      setIsLoading(false);
    }
  };

  // 답변 전송
  const sendResponse = async () => {
    if (!userInput.trim() || isLoading) return;

    const userMessage = userInput.trim();
    setUserInput('');
    
    // 사용자 메시지 추가
    addMessage({
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    });

    setIsLoading(true);

    try {
      console.log('사용자 응답 전송:', { session_id: actualSessionId || sessionId, response: userMessage });
      
      // 백엔드에 사용자 응답 전송
      const response = await axios.post('http://localhost:8000/api/interview/respond', {
        session_id: actualSessionId || sessionId,
        response: userMessage
      });

      console.log('AI 응답:', response.data);

      const aiResponse = response.data.question || response.data.response || "흥미로운 답변이네요. 더 자세히 설명해 주실 수 있나요?";

      // AI 응답 추가
      addMessage({
        role: 'assistant',
        content: aiResponse,
        timestamp: new Date().toISOString()
      });

      setCurrentQuestion(aiResponse);

    } catch (error) {
      console.error('응답 전송 실패:', error);
      
      // 간단한 AI 응답 생성 (백엔드 실패시 폴백)
      const fallbackResponses = [
        "흥미로운 답변이네요. 조금 더 구체적으로 설명해 주실 수 있나요?",
        "좋은 경험이었을 것 같습니다. 그 과정에서 어떤 어려움이 있었나요?",
        "훌륭합니다. 그 경험을 통해 무엇을 배웠나요?",
        "이해했습니다. 앞으로의 계획은 어떻게 되시나요?"
      ];
      
      const fallbackResponse = fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)];
      
      addMessage({
        role: 'assistant',
        content: fallbackResponse,
        timestamp: new Date().toISOString()
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 면접 종료
  const endInterview = async () => {
    try {
      const response = await axios.post(`http://localhost:8000/api/interview/end?session_id=${actualSessionId || sessionId}`);

      onInterviewEnd({
        feedback: response.data.feedback || "면접이 완료되었습니다. 수고하셨습니다!",
        session_id: actualSessionId || sessionId,
        analysis: response.data
      });
    } catch (error) {
      console.error('면접 종료 실패:', error);
      onInterviewEnd({
        feedback: "면접이 완료되었습니다. 수고하셨습니다!",
        session_id: actualSessionId || sessionId
      });
    }
  };

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg flex flex-col h-[600px]">
      {/* 헤더 */}
      <div className="bg-blue-600 text-white p-4 rounded-t-lg">
        <h2 className="text-xl font-bold">AI 면접관과의 대화</h2>
        <p className="text-blue-100 text-sm">
          {profile?.institution && `${profile.institution} 면접`}
          {profile?.type && ` - ${profile.type === 'gifted_center' ? '영재교육원' : 
                                  profile.type === 'science_high' ? '영재학교/과학고' : 
                                  profile.type === 'university' ? '대학입시' :
                                  profile.type === 'quiz' ? '퀴즈' : '기타'}`}
        </p>
      </div>

      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[70%] p-3 rounded-lg ${
              message.role === 'user' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              <div className="flex items-start space-x-2">
                <span className="text-sm font-medium">
                  {message.role === 'user' ? '나' : 'AI 면접관'}
                </span>
              </div>
              <p className="mt-1 whitespace-pre-wrap">{message.content}</p>
              <p className="text-xs opacity-70 mt-1">
                {new Date(message.timestamp).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 p-3 rounded-lg">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium">AI 면접관</span>
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 입력 영역 */}
      <div className="border-t p-4">
        <div className="flex space-x-3">
          <textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendResponse();
              }
            }}
            placeholder="답변을 입력하세요... (Shift+Enter로 줄바꿈)"
            className="flex-1 p-3 border rounded resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
            disabled={isLoading}
          />
          <div className="flex flex-col space-y-2">
            <button
              onClick={sendResponse}
              disabled={!userInput.trim() || isLoading}
              className={`px-6 py-2 rounded ${
                userInput.trim() && !isLoading
                  ? 'bg-blue-500 text-white hover:bg-blue-600'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {isLoading ? '전송중...' : '답변 전송'}
            </button>
            <button
              onClick={endInterview}
              className="px-6 py-2 bg-red-500 text-white rounded hover:bg-red-600"
            >
              면접 종료
            </button>
          </div>
        </div>
        
        {/* 도움말 */}
        <div className="mt-2 text-xs text-gray-500">
          <p>💡 팁: 구체적이고 솔직한 답변을 해주세요. Enter로 전송, Shift+Enter로 줄바꿈</p>
          {profile?.fields?.length > 0 && (
            <p>관심 영역: {profile.fields.join(', ')}</p>
          )}
        </div>
      </div>

      {/* 세션 정보 */}
      <div className="text-xs text-gray-400 px-4 pb-2">
        세션 ID: {actualSessionId || sessionId}
      </div>
    </div>
  );
};

export default InterviewChat;
