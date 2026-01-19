/**
 * 📄 파일명: main.jsx
 * 📝 설명: React 애플리케이션 엔트리 포인트 - 앱을 DOM에 마운트합니다
 * 🔗 API: 없음
 * ✏️ 수정 시 주의: 이 파일은 거의 수정할 일이 없습니다
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
)
