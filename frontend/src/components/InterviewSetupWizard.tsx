import React, { useState } from 'react';
import axios from 'axios';

// majors_list.json에서 추출한 계열 데이터
const MAJOR_FIELDS = [
  '인문학',
  '사회과학', 
  '자연과학',
  '공학',
  '교육학',
  '의료',
  '예체능',
  '생태학',
  '정보·데이터과학',
  '융합창업',
  '미디어디자인'
];

// 면접 유형별 기관명 예시 매핑
const INSTITUTION_EXAMPLES = {
  'gifted_center': [
    '서울시교육청 영재교육원',
    '경기도교육청 영재교육원', 
    '부산광역시교육청 영재교육원',
    '인천광역시교육청 영재교육원'
  ],
  'science_high': [
    '서울과학고등학교',
    '경기과학고등학교',
    '대구과학고등학교',
    '한국과학영재학교'
  ],
  'university': [
    '서울대학교',
    '연세대학교',
    '고려대학교',
    'KAIST',
    'POSTECH'
  ],
  'quiz': [
    '퀴즈대회',
    '과학경시대회',
    '수학올림피아드',
    '토론대회'
  ],
  'other': [
    '면접 기관명',
    '지원 기관',
    '목표 기관'
  ]
};

// 면접 유형별 난이도 매핑
const DIFFICULTY_MAPPING = {
  'gifted_center': 'elementary',  // 초등 수준
  'science_high': 'middle',       // 중등 수준  
  'university': 'high',           // 고등 수준
  'quiz': 'middle',               // 중등 수준
  'other': 'high'                 // 고등 수준 (기본)
};

interface InterviewSetupWizardProps {
  onComplete: (profile: any) => void;
  onCancel: () => void;
}

const InterviewSetupWizard: React.FC<InterviewSetupWizardProps> = ({ onComplete, onCancel }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [profile, setProfile] = useState({
    type: '',
    institution: '',
    fields: '', // 단일 선택으로 변경
    keywords: [] as string[],
    additionalStyle: '',
    uploadedFiles: [] as any[],
    difficulty: '' // 난이도 추가
  });

  const [keywordInput, setKeywordInput] = useState('');

  const addKeyword = () => {
    if (keywordInput.trim() && !profile.keywords.includes(keywordInput.trim())) {
      setProfile({ ...profile, keywords: [...profile.keywords, keywordInput.trim()] });
      setKeywordInput('');
    }
  };

  const removeKeyword = (keyword: string) => {
    setProfile({ ...profile, keywords: profile.keywords.filter(k => k !== keyword) });
  };

  // 다음 단계로
  const nextStep = () => {
    if (currentStep < 6) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  // 이전 단계로
  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  // 완료 처리
  const handleComplete = async () => {
    try {
      // 백엔드에 프로필 저장
      const response = await axios.post('http://localhost:8000/api/interview/profile', {
        profile: {
          ...profile,
          fields: profile.fields ? [profile.fields] : [], // 백엔드 호환성을 위해 배열로 변환
          difficulty: profile.difficulty
        }
      });

      console.log('프로필 저장 완료:', response.data);
      
      // 개인화된 면접 시작
      onComplete({
        ...profile,
        fields: profile.fields ? [profile.fields] : [], // 백엔드 호환성을 위해 배열로 변환
        profileId: response.data.profile_id
      });
    } catch (error) {
      console.error('프로필 저장 실패:', error);
      // 에러가 있어도 일단 면접은 시작하도록
      onComplete({
        ...profile,
        fields: profile.fields ? [profile.fields] : [],
        difficulty: profile.difficulty
      });
    }
  };

  // 현재 단계가 완료 가능한지 체크
  const canProceed = () => {
    switch (currentStep) {
      case 1: return profile.type !== '';
      case 2: return profile.institution.trim() !== '';
      case 3: return profile.fields !== '';
      case 4: return true; // 키워드는 선택사항
      case 5: return true; // 파일은 선택사항
      case 6: return true; // 추가 스타일은 선택사항
      default: return false;
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
      {/* 진행률 표시 */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-500 mb-2">
          <span>단계 {currentStep} / 6</span>
          <span>{Math.round((currentStep / 6) * 100)}% 완료</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(currentStep / 6) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* 현재 단계 내용 */}
      <div className="mb-8 min-h-[300px]">
        {/* 1단계: 면접 유형 선택 */}
        {currentStep === 1 && (
          <div>
            <h3 className="text-xl font-semibold mb-4">원하는 면접 유형을 선택하세요.</h3>
            <div className="space-y-3">
              {[
                { value: 'gifted_center', label: '영재교육원 면접', difficulty: '초등 수준' },
                { value: 'science_high', label: '영재학교, 과학고 면접', difficulty: '중등 수준' },
                { value: 'university', label: '대학 입시 면접', difficulty: '고등 수준' },
                { value: 'quiz', label: '퀴즈', difficulty: '중등 수준' },
                { value: 'other', label: '기타', difficulty: '고등 수준' }
              ].map((option) => (
                <label key={option.value} className="flex items-center p-3 border rounded cursor-pointer hover:bg-blue-50">
                  <input
                    type="radio"
                    name="type"
                    value={option.value}
                    checked={profile.type === option.value}
                    onChange={(e) => {
                      const newType = e.target.value;
                      const newDifficulty = DIFFICULTY_MAPPING[newType as keyof typeof DIFFICULTY_MAPPING] || 'high';
                      setProfile(prev => ({ 
                        ...prev, 
                        type: newType,
                        difficulty: newDifficulty
                      }));
                    }}
                    className="mr-3"
                  />
                  <div className="flex-1">
                    <span className="text-lg">{option.label}</span>
                    <span className="text-sm text-gray-500 block">({option.difficulty})</span>
                  </div>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* 2단계: 기관명 입력 */}
        {currentStep === 2 && (
          <div>
            <h3 className="text-xl font-semibold mb-4">지원하는 기관명을 입력하세요.</h3>
            <input
              key="institution-input"
              type="text"
              value={profile.institution}
              onChange={(e) => setProfile(prev => ({ ...prev, institution: e.target.value }))}
              className="w-full p-3 border rounded text-lg"
              placeholder={`예) ${profile.type && INSTITUTION_EXAMPLES[profile.type as keyof typeof INSTITUTION_EXAMPLES] 
                ? INSTITUTION_EXAMPLES[profile.type as keyof typeof INSTITUTION_EXAMPLES][0] 
                : '지원 기관명'}`}
              autoFocus
            />
            <p className="text-sm text-gray-500 mt-2">
              정확한 기관명을 입력해주세요. 
              {profile.type && INSTITUTION_EXAMPLES[profile.type as keyof typeof INSTITUTION_EXAMPLES] && (
                <span className="block mt-1">
                  추천: {INSTITUTION_EXAMPLES[profile.type as keyof typeof INSTITUTION_EXAMPLES].slice(0, 3).join(', ')}
                </span>
              )}
            </p>
          </div>
        )}

        {/* 3단계: 관심 영역 선택 (단일 선택) */}
        {currentStep === 3 && (
          <div>
            <h3 className="text-xl font-semibold mb-4">관심있는 영역 및 진로희망을 선택하세요.</h3>
            <div className="grid grid-cols-3 gap-3">
              {MAJOR_FIELDS.map((field) => (
                <label key={field} className="flex items-center p-2 border rounded cursor-pointer hover:bg-blue-50 transition-colors">
                  <input
                    type="radio"
                    name="fields"
                    value={field}
                    checked={profile.fields === field}
                    onChange={(e) => setProfile(prev => ({ ...prev, fields: e.target.value }))}
                    className="mr-2"
                  />
                  <span className="text-sm font-medium">{field}</span>
                </label>
              ))}
            </div>
            <p className="text-sm text-gray-500 mt-3">
              관심 분야 하나를 선택해주세요. 이 정보는 맞춤형 면접 질문 생성에 활용됩니다.
            </p>
            {profile.fields && (
              <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-700">
                  ✅ 선택된 분야: <strong>{profile.fields}</strong>
                </p>
              </div>
            )}
          </div>
        )}

        {/* 4단계: 키워드 입력 */}
        {currentStep === 4 && (
          <div>
            <h3 className="text-xl font-semibold mb-4">관심있는 주제의 키워드를 입력하세요.</h3>
            <div className="flex mb-3">
              <input
                key="keyword-input"
                type="text"
                value={keywordInput}
                onChange={(e) => setKeywordInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addKeyword()}
                className="flex-1 p-3 border rounded-l"
                placeholder="예) 양자역학, 인공지능, 생명과학 등"
              />
              <button
                onClick={addKeyword}
                className="px-4 py-3 bg-blue-600 text-white rounded-r hover:bg-blue-700"
              >
                추가
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {profile.keywords.map((keyword) => (
                <span key={keyword} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm flex items-center">
                  {keyword}
                  <button
                    onClick={() => removeKeyword(keyword)}
                    className="ml-2 text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <p className="text-sm text-gray-500 mt-3">여러 개의 키워드를 입력할 수 있습니다. (선택사항)</p>
          </div>
        )}

        {/* 5단계: 파일 업로드 */}
        {currentStep === 5 && (
          <div>
            <h3 className="text-xl font-semibold mb-4">자기소개서 또는 탐구 보고서가 있다면 파일을 업로드해주세요.</h3>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <input
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.hwp"
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <div className="text-gray-500">
                  <p className="text-lg mb-2">파일을 드래그하거나 클릭하여 업로드</p>
                  <p className="text-sm">업로드 가능한 파일 형식: hwp(x), doc(x), pdf, xlsx, txt</p>
                </div>
              </label>
            </div>
            <p className="text-sm text-gray-500 mt-3">파일 업로드는 선택사항입니다.</p>
          </div>
        )}

        {/* 6단계: 추가 스타일 요청 */}
        {currentStep === 6 && (
          <div>
            <h3 className="text-xl font-semibold mb-4">추가 구체적으로 원하는 스타일이 있다면 작성해주세요.</h3>
            <textarea
              key="style-textarea"
              value={profile.additionalStyle}
              onChange={(e) => setProfile(prev => ({ ...prev, additionalStyle: e.target.value }))}
              className="w-full p-3 border rounded text-lg h-32"
              placeholder="예) 관심이 있는 주제 위주로 질문해 주세요, 초등학생 수준으로 맞춰 주세요"
              autoFocus
            />
            <p className="text-sm text-gray-500 mt-2">이 내용은 선택사항입니다.</p>
          </div>
        )}
      </div>

      {/* 네비게이션 버튼 */}
      <div className="flex justify-between">
        <button
          onClick={currentStep === 1 ? onCancel : prevStep}
          className="px-6 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
        >
          {currentStep === 1 ? '취소' : '이전'}
        </button>
        
        <button
          onClick={nextStep}
          disabled={!canProceed()}
          className={`px-6 py-2 rounded ${
            canProceed()
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {currentStep === 6 ? '면접 시작' : '다음'}
        </button>
      </div>
    </div>
  );
};

export default InterviewSetupWizard;
