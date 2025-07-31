import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  // 개발 중 중복 API 호출 방지를 위해 임시로 StrictMode 비활성화
  // <React.StrictMode>
    <App />
  // </React.StrictMode>
); 