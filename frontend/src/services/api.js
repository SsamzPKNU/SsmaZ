/**
 * API 통신을 위한 서비스 파일
 * Axios를 사용하여 백엔드와 통신합니다
 * 
 * 보안 방식:
 * - JWT 토큰: httpOnly 쿠키로 저장 (XSS 방지)
 * - CSRF 토큰: localStorage에 저장, 매 요청 시 헤더로 전송
 */

import axios from 'axios';

// Axios 인스턴스 생성
const api = axios.create({
    baseURL: 'http://192.168.0.35:8000', // 백엔드 서버 주소
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true, // httpOnly 쿠키 전송을 위해 필수
});

// 요청 인터셉터: 모든 요청에 CSRF 토큰 자동 추가
api.interceptors.request.use(
    (config) => {
        // localStorage에서 CSRF 토큰 가져오기
        const csrfToken = localStorage.getItem('csrf_token');

        // CSRF 토큰이 있으면 X-CSRF-Token 헤더에 추가
        if (csrfToken) {
            config.headers['X-CSRF-Token'] = csrfToken;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 응답 인터셉터: 401/403 에러 시 로그인 페이지로 리다이렉트
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // 401 Unauthorized 또는 403 Forbidden 에러 처리
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
            // CSRF 토큰과 사용자 정보 삭제
            localStorage.removeItem('csrf_token');
            localStorage.removeItem('user');

            // 로그인 페이지로 이동 (현재 페이지가 로그인 페이지가 아닌 경우에만)
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }

        return Promise.reject(error);
    }
);

/**
 * 회원가입 API
 * @param {Object} userData - 회원가입 정보
 * @param {string} userData.username - 로그인 ID
 * @param {string} userData.password - 비밀번호 (최소 8자, 영문+숫자 필수)
 * @param {number} userData.academy_id - 학원 ID
 * @param {string} userData.user_role - 사용자 역할 (ADMIN/TEACHER/STUDENT)
 * @param {string} userData.name - 실명 (선택)
 * @param {string} userData.phone - 전화번호 (선택)
 * @returns {Promise} 생성된 사용자 정보
 */
export const signup = async (userData) => {
    const response = await api.post('/auth/signup', userData);
    return response.data;
};

/**
 * 로그인 API
 * 
 * 성공 시:
 * - JWT 토큰이 httpOnly 쿠키로 자동 저장됨
 * - CSRF 토큰은 응답 body로 반환되어 localStorage에 저장
 * 
 * @param {Object} credentials - 로그인 정보
 * @param {string} credentials.username - 로그인 ID
 * @param {string} credentials.password - 비밀번호
 * @returns {Promise} CSRF 토큰 및 사용자 정보
 */
export const login = async (credentials) => {
    const response = await api.post('/auth/login', credentials);

    // 응답 데이터 구조: { csrf_token, token_type, user }
    const { csrf_token, user } = response.data;

    // CSRF 토큰과 사용자 정보를 localStorage에 저장
    // (JWT 토큰은 httpOnly 쿠키로 자동 저장됨)
    localStorage.setItem('csrf_token', csrf_token);
    localStorage.setItem('user', JSON.stringify(user));

    return response.data;
};

/**
 * 로그아웃 API
 * 
 * - 서버에 로그아웃 요청 (httpOnly 쿠키 삭제)
 * - localStorage에서 CSRF 토큰과 사용자 정보 삭제
 */
export const logout = async () => {
    try {
        // 서버에 로그아웃 요청 (쿠키 삭제)
        await api.post('/auth/logout');
    } catch (error) {
        // 에러가 발생해도 클라이언트 측 정리는 진행
        console.error('로그아웃 요청 실패:', error);
    }

    // 클라이언트 측 정리
    localStorage.removeItem('csrf_token');
    localStorage.removeItem('user');
};

/**
 * 현재 로그인한 사용자 정보 가져오기
 * @returns {Object|null} 사용자 정보 또는 null
 */
export const getCurrentUser = () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
};

/**
 * 현재 사용자 정보 서버에서 새로 가져오기
 * @returns {Promise} 사용자 정보
 */
export const fetchCurrentUser = async () => {
    const response = await api.get('/auth/me');

    // 사용자 정보 업데이트
    localStorage.setItem('user', JSON.stringify(response.data));

    return response.data;
};

/**
 * 로그인 여부 확인
 * 
 * CSRF 토큰이 존재하면 로그인 상태로 간주
 * (httpOnly 쿠키는 JavaScript에서 확인 불가)
 * 
 * @returns {boolean} 로그인 상태
 */
export const isAuthenticated = () => {
    return !!localStorage.getItem('csrf_token');
};

/**
 * CSRF 토큰 가져오기
 * @returns {string|null} CSRF 토큰 또는 null
 */
export const getCsrfToken = () => {
    return localStorage.getItem('csrf_token');
};

export default api;
