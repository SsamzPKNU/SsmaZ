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
    baseURL: 'http://192.168.0.35:8000', // 백엔드 서버 주소 (Vite 프록시 사용)
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
 * 백엔드 (Coding Kit Shop) 구조에 맞춰 데이터 매핑
 */
export const signup = async (userData) => {
    // 백엔드 API 변경: /auth/signup
    // username, password, academy_id, user_role, name, phone 전송
    const payload = {
        username: userData.username,
        password: userData.password,
        academy_id: userData.academy_id,
        user_role: userData.user_role,
        name: userData.name,
        phone: userData.phone
    };

    const response = await api.post('/auth/signup', payload);
    return response.data;
};

/**
 * 로그인 API
 * 백엔드 (/api/auth/login) 호출
 */
export const login = async (credentials) => {
    // 백엔드는 username, password 필요
    const payload = {
        username: credentials.username,
        password: credentials.password
    };

    const response = await api.post('/auth/login', payload);

    // 응답: { access_token }
    // Shop 백엔드는 JWT만 반환하고 User 정보는 반환하지 않음 (이후 fetchCurrentUser로 가져와야 함 하지만 일단 username 저장)
    const { access_token } = response.data;

    // 이 백엔드는 CSRF 토큰을 별도로 주지 않고 JWT 방식을 사용하는 것으로 보임.
    // 기존 로직 유지를 위해 localStorage에 토큰 저장 (CSRF 토큰 대용으로 사용하거나 로직 수정 필요)
    // 여기서는 isAuthenticated()가 CSRF 토큰 유무를 체크하므로, access_token을 저장.
    localStorage.setItem('csrf_token', access_token);

    // 임시 사용자 정보 저장 (백엔드가 User 객체를 주지 않으므로)
    const user = { username: credentials.username, name: 'User', role: 'ADMIN' };
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
