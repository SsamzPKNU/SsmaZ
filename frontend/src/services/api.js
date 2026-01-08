/**
 * API 통신을 위한 서비스 파일
 * Axios를 사용하여 백엔드와 통신합니다
 */

import axios from 'axios';

// Axios 인스턴스 생성
const api = axios.create({
    baseURL: 'http://localhost:8000', // 백엔드 서버 주소
    headers: {
        'Content-Type': 'application/json',
    },
});

// 요청 인터셉터: 모든 요청에 JWT 토큰 자동 추가
api.interceptors.request.use(
    (config) => {
        // localStorage에서 토큰 가져오기
        const token = localStorage.getItem('access_token');

        // 토큰이 있으면 Authorization 헤더에 추가
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 응답 인터셉터: 401 에러 시 로그인 페이지로 리다이렉트
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // 401 Unauthorized 에러 처리
        if (error.response && error.response.status === 401) {
            // 토큰 삭제
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');

            // 로그인 페이지로 이동
            window.location.href = '/login';
        }

        return Promise.reject(error);
    }
);

/**
 * 회원가입 API
 * @param {Object} userData - 회원가입 정보
 * @param {string} userData.username - 로그인 ID
 * @param {string} userData.password - 비밀번호
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
 * @param {Object} credentials - 로그인 정보
 * @param {string} credentials.username - 로그인 ID
 * @param {string} credentials.password - 비밀번호
 * @returns {Promise} JWT 토큰 및 사용자 정보
 */
export const login = async (credentials) => {
    const response = await api.post('/auth/login', credentials);

    // 응답 데이터 구조: { access_token, token_type, user }
    const { access_token, user } = response.data;

    // localStorage에 토큰과 사용자 정보 저장
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('user', JSON.stringify(user));

    return response.data;
};

/**
 * 로그아웃
 * localStorage에서 토큰과 사용자 정보 삭제
 */
export const logout = () => {
    localStorage.removeItem('access_token');
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
 * 로그인 여부 확인
 * @returns {boolean} 로그인 상태
 */
export const isAuthenticated = () => {
    return !!localStorage.getItem('access_token');
};

export default api;
