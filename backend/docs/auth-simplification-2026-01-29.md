# 인증 방식 간략화 변경사항

**변경일**: 2026-01-29
**변경 파일**: `app/api/auth.py`
**목적**: 개발 편의성을 위한 CSRF 토큰 검증 임시 비활성화

---

## 변경 배경

개발 환경에서 CSRF 토큰 관리로 인한 인증 문제가 발생하여, 개발 편의성을 위해 CSRF 검증을 임시로 비활성화했습니다.

> **주의**: 프로덕션 배포 전 반드시 CSRF 검증을 다시 활성화해야 합니다.

---

## 변경 내용

### 1. CSRF 토큰 검증 비활성화 (60-73라인)

`get_current_user` 함수에서 CSRF 토큰 검증 로직을 주석 처리했습니다.

```python
# 변경 전
if access_token:
    token = access_token

    csrf_token = request.headers.get("X-CSRF-Token")

    if not csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF 토큰이 필요합니다",
        )

    if not verify_csrf_token(token, csrf_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF 토큰이 유효하지 않습니다",
        )

# 변경 후
if access_token:
    token = access_token

    # [개발용 비활성화] CSRF 토큰 검증 (쿠키 방식일 때만)
    # csrf_token = request.headers.get("X-CSRF-Token")
    # ... (주석 처리됨)
```

### 2. 토큰 생성 방식 변경 (230-232라인)

CSRF 토큰 포함 토큰 대신 일반 토큰만 생성합니다.

```python
# 변경 전
access_token, csrf_token = AuthService.create_user_token_with_csrf(user)

# 변경 후
# [개발용 변경] CSRF 토큰 없이 일반 토큰만 생성
# access_token, csrf_token = AuthService.create_user_token_with_csrf(user)
access_token = AuthService.create_user_token(user)
```

### 3. 쿠키 설정 간소화 (235-243라인)

HTTP 환경에서도 쿠키가 동작하도록 설정을 변경했습니다.

```python
# 변경 전
response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    secure=IS_PRODUCTION,  # HTTPS에서만 전송 (프로덕션)
    samesite="strict" if IS_PRODUCTION else "lax",
    max_age=30 * 60,
    path="/"
)

# 변경 후
response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    secure=False,  # [개발용] HTTP에서도 동작
    samesite="lax",  # [개발용] 크로스 사이트 허용
    max_age=30 * 60,
    path="/"
)
```

### 4. 로그인 응답 csrf_token 빈 값 처리 (246-250라인)

```python
# 변경 전
return Token(
    csrf_token=csrf_token,
    token_type="bearer",
    user=UserResponse.from_orm(user)
)

# 변경 후
return Token(
    csrf_token="",  # [개발용] CSRF 토큰 비활성화
    token_type="bearer",
    user=UserResponse.from_orm(user)
)
```

---

## 프론트엔드 영향

- 로그인 응답의 `csrf_token` 값이 빈 문자열(`""`)로 반환됩니다.
- API 호출 시 `X-CSRF-Token` 헤더를 전송하지 않아도 됩니다.
- 쿠키 기반 인증만으로 모든 API 호출이 가능합니다.

---

## 테스트 방법

```bash
# 서버 재시작
python main.py
```

1. 관리자 로그인 → 메인화면 유지 확인
2. 학생 로그인 → 결제 API 호출 성공 확인
3. 선생님 로그인 → 기존처럼 정상 동작 확인

---

## 프로덕션 배포 전 체크리스트

- [ ] CSRF 토큰 검증 주석 해제
- [ ] `secure=IS_PRODUCTION` 복원
- [ ] `samesite="strict" if IS_PRODUCTION else "lax"` 복원
- [ ] `csrf_token` 정상 반환 복원

---

## 관련 파일

- `app/api/auth.py` - 인증 API
- `app/services/auth_service.py` - 인증 서비스 (토큰 생성)
- `app/core/security.py` - 보안 유틸리티 (CSRF 검증)
