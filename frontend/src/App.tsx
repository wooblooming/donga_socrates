import React, { useState } from 'react';
import { useInterviewStore } from './store/interviewStore';
import InterviewChat from './components/InterviewChat';
import InterviewSetupWizard from './components/InterviewSetupWizard';

function App() {
  const [currentSession, setCurrentSession] = useState<string | null>(null);
  const [showWizard, setShowWizard] = useState(false);
  const [currentProfile, setCurrentProfile] = useState<any>(null);
  const { clearMessages } = useInterviewStore();

  const handleStartSetup = () => {
    setShowWizard(true);
  };

  const handleWizardCancel = () => {
    setShowWizard(false);
  };

  const handleWizardComplete = (profile: any) => {
    clearMessages();
    const sessionId = 'session-' + Date.now();
    setCurrentSession(sessionId);
    setCurrentProfile(profile);
    setShowWizard(false);
  };

  const handleInterviewEnd = (analysis: any) => {
    alert(analysis.feedback);
    setCurrentSession(null);
  };

  const handleBackToHome = () => {
    setCurrentSession(null);
    setCurrentProfile(null);
    setShowWizard(false);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <button
            onClick={handleBackToHome}
            className="text-2xl font-bold text-blue-600 hover:text-blue-800"
          >
            🤖 AI 면접관
          </button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {!currentSession && !showWizard ? (
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-800 mb-4">
              AI와 함께하는 면접 연습
            </h1>
            <p className="text-gray-600 mb-8">
              개인 맞춤형 AI 면접관과 실전 같은 면접을 연습해보세요.
            </p>
            <button
              onClick={handleStartSetup}
              className="px-6 py-3 bg-blue-600 text-white text-lg rounded-lg hover:bg-blue-700"
            >
              면접 시작하기
            </button>
          </div>
        ) : showWizard ? (
          <InterviewSetupWizard
            onComplete={handleWizardComplete}
            onCancel={handleWizardCancel}
          />
        ) : (
          <InterviewChat
            sessionId={currentSession}
            onInterviewEnd={handleInterviewEnd}
            profile={currentProfile}
          />
        )}
      </main>
    </div>
  );
}

export default App;
