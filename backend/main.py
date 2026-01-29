from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.text_review import ReviewRequest, ReviewResponse, HealthResponse
from app.services.text_review.review_generator import ReviewGenerator

# API 라우터 임포트
from app.api.auth import router as auth_router
from app.api.attendance import router as attendance_router
from app.api.kiosk import router as kiosk_router
from app.api.dashboard import router as dashboard_router
from app.api.teacher import router as teacher_router
from app.api.student import router as student_router
from app.api.payment import router as payment_router
from app.api.toss import router as toss_router
from app.api.message import router as message_router
from app.api.class_api import router as class_router
from app.api.teacher_app import router as teacher_app_router
from app.api.student_contact import router as student_contact_router
from app.api.teacher_attendance import router as teacher_attendance_router
from app.api.admin_attendance import router as admin_attendance_router
from app.api.assignments import router as assignments_router
from app.api.submissions import router as submissions_router
from app.api.clinic import router as clinic_router
from app.api.pdf import router as pdf_router
from app.api.support import router as support_router
from app.api.invoice import router as invoice_router
from app.api.student_payment import router as student_payment_router

# 데이터베이스 및 모델 임포트 (테이블 자동 생성용)
from app.core.database import engine, Base
from app.models.user import User
from app.models.login_log import LoginLog
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.payment import Payment
from app.models.message import Message
from app.models.class_model import Class
from app.models.attendance import Attendance
from app.models.student_contact import StudentContact
from app.models.teacher_attendance import TeacherAttendance
from app.models.assignment import Assignment, Question
from app.models.submission import Submission, Answer
from app.models.question_bank import QuestionBank
from app.models.schedule import Schedule
from app.models.support import Inquiry, FAQ, Notice
from app.models.invoice import Invoice

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Rate Limiter 설정 (IP 기반)
limiter = Limiter(key_func=get_remote_address)

# 데이터베이스 테이블 생성
# 앱 시작 시 모든 모델의 테이블을 자동으로 생성합니다
Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI(
    title="학원 관리 서비스 SsmaZ API",
    description="학원 수업 리뷰 생성 및 관리자 관리 기능을 제공합니다",
    version="1.0.0"
)

# Rate Limiter 등록
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# CORS 설정 (라우터보다 먼저 등록)
# httpOnly 쿠키 전송을 위해 credentials=True 설정
# 개발환경: 모든 origin 동적 허용, 프로덕션: 명시적 origin만 허용
if ENVIRONMENT == "development":
    # allow_origin_regex로 모든 origin 매칭 (credentials와 함께 사용 가능)
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r".*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Set-Cookie"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Set-Cookie"],
    )

# 라우터 등록
app.include_router(auth_router)
app.include_router(attendance_router, prefix="/attendance", tags=["Attendance"])
app.include_router(kiosk_router)  # 키오스크 라우터 (prefix는 라우터 내부에 정의됨)
app.include_router(dashboard_router)  # 대시보드 라우터
app.include_router(teacher_router)  # 선생님 관리 라우터
app.include_router(student_router)  # 학생 관리 라우터
app.include_router(payment_router)  # 수납/결제 관리 라우터
app.include_router(toss_router)  # 토스페이먼츠 연동 라우터
app.include_router(message_router)  # 메시지 센터 라우터
app.include_router(class_router)  # 클래스 관리 라우터
app.include_router(teacher_app_router)  # 선생님용 앱 라우터
app.include_router(student_contact_router)  # 학생 연락처 관리 라우터
app.include_router(teacher_attendance_router)  # 선생님 출퇴근 라우터
app.include_router(admin_attendance_router)  # 관리자용 출퇴근 승인 라우터
app.include_router(assignments_router, prefix="/api/assignments", tags=["Assignments"])
app.include_router(submissions_router, prefix="/api/submissions", tags=["Submissions"])
app.include_router(clinic_router, prefix="/api/clinic", tags=["Clinic"])
app.include_router(pdf_router, prefix="/api/pdf", tags=["PDF"])
app.include_router(support_router)  # 상담/문의 관리 라우터
app.include_router(invoice_router)  # 청구서 관리 라우터
app.include_router(student_payment_router)  # 학생 결제 라우터

# ReviewGenerator 인스턴스 생성
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "student-review")

review_generator = ReviewGenerator(
    ollama_url=OLLAMA_URL,
    model_name=MODEL_NAME
)


@app.get("/", tags=["Root"])
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "학원 관리 서비스 SsmaZ API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "signup": "/auth/signup",
            "login": "/auth/login",
            "generate_review": "/api/review/generate",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """헬스 체크 및 Ollama 연결 확인"""
    ollama_connected = await review_generator.check_connection()
    
    return HealthResponse(
        status="healthy" if ollama_connected else "unhealthy",
        ollama_connected=ollama_connected,
        model_name=MODEL_NAME
    )


@app.post("/api/review/generate", response_model=ReviewResponse, tags=["Review"])
async def generate_review(request: ReviewRequest):
    """
    수업 리뷰 문자 메시지 생성
    
    - **student_name**: 학생 이름
    - **parent_name**: 학부모 이름 (선택, 없으면 학생 이름 사용)
    - **learning_content**: 오늘 배운 학습 내용
    - **attitude**: 학생의 수업 태도
    """
    
    # Ollama 연결 확인
    if not await review_generator.check_connection():
        raise HTTPException(
            status_code=503,
            detail="Ollama 서버에 연결할 수 없습니다. Ollama가 실행 중인지 확인해주세요."
        )
    
    # 리뷰 생성
    result = await review_generator.generate_review(
        student_name=request.student_name,
        parent_name=request.parent_name or request.student_name,
        learning_content=request.learning_content,
        attitude=request.attitude
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result["error"]
        )
    
    return ReviewResponse(
        success=True,
        message=result["message"],
        error=None
    )


@app.get("/api/review/test", tags=["Review"])
async def test_review():
    """테스트용 샘플 리뷰 생성"""
    sample_request = ReviewRequest(
        student_name="김민수",
        parent_name="김민수",
        learning_content="영어 문법 - 현재완료 시제를 배웠습니다",
        attitude="집중력이 좋았고 질문도 적극적으로 했습니다"
    )
    
    return await generate_review(sample_request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
