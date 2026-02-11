import os
from dotenv import load_dotenv

# 다른 모듈 import 전에 환경 변수 먼저 로드
load_dotenv()

import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
from app.api.student_portal import router as student_portal_router
from app.api.teacher_assignment import router as teacher_assignment_router
from app.api.teacher_analytics import router as teacher_analytics_router
from app.api.teacher_clinic import router as teacher_clinic_router
from app.api.teacher_message import router as teacher_message_router
from app.api.teacher_print import router as teacher_print_router
from app.api.chat import router as chat_router
from app.api.fcm_token import router as fcm_token_router
from app.services.faq_loader import load_faq_to_chromadb
from app.services.chat_service import get_chat_service
from app.services.push_notification_service import PushNotificationService
import asyncio
import json

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
from app.models.message_template import MessageTemplate
from app.models.message_recipient import MessageRecipient
from app.models.class_teacher import ClassTeacherAssignment
from app.models.fcm_token import FCMToken

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

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
app.include_router(student_portal_router)  # 학생 포털 라우터
app.include_router(teacher_assignment_router)  # 선생님 과제/채점 라우터
app.include_router(teacher_analytics_router)  # 선생님 오답 분석 라우터
app.include_router(teacher_clinic_router)  # 선생님 클리닉 라우터
app.include_router(teacher_message_router)  # 선생님 메시지 라우터
app.include_router(teacher_print_router)  # 선생님 프린트 라우터
app.include_router(chat_router)  # FAQ 챗봇 라우터
app.include_router(fcm_token_router)  # FCM 토큰 관리 라우터

# ReviewGenerator 인스턴스 생성
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama31:latest")

review_generator = ReviewGenerator(
    ollama_url=OLLAMA_URL,
    model_name=MODEL_NAME
)


async def warm_up_faq_background():
    """
    FAQ 챗봇 Warm-up (백그라운드)

    서버 시작 후 1초 대기 후 FAQ 질문에 대한 답변을 사전 생성
    이를 통해 첫 사용자 요청의 지연을 최소화
    """
    # 서버 완전 시작 후 1초 대기
    await asyncio.sleep(1)

    print("[FAQ Warm-up] 백그라운드 Warm-up 시작...")

    try:
        # FAQ 데이터 로드
        faq_path = os.path.join(os.path.dirname(__file__), "app", "data", "faq_data.json")
        if not os.path.exists(faq_path):
            print(f"[FAQ Warm-up] FAQ 파일 없음: {faq_path}")
            return

        with open(faq_path, 'r', encoding='utf-8') as f:
            faq_data = json.load(f)

        # ChatService warm-up 실행
        chat_service = get_chat_service()
        cached_count = chat_service.warm_up_faq(faq_data)

        print(f"[FAQ Warm-up] 완료: {cached_count}개 질문 캐싱됨")

    except Exception as e:
        print(f"[FAQ Warm-up] 오류 발생: {e}")


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화"""
    # FAQ 데이터 로드
    print("[Startup] FAQ 데이터 로드 시작...")
    success = load_faq_to_chromadb()
    if success:
        print("[Startup] FAQ 데이터 로드 완료")
    else:
        print("[Startup] FAQ 데이터 로드 실패 - 챗봇 기능이 제한될 수 있습니다")

    # Ollama 모델 Warm-up
    print("[Startup] Ollama 모델 Warm-up 시작...")
    warmup_success = await review_generator.warm_up()
    if warmup_success:
        print("[Startup] Ollama 모델 Warm-up 완료")
    else:
        print("[Startup] Ollama 모델 Warm-up 실패 - 첫 요청 시 지연 발생 가능")

    # Firebase Admin SDK 초기화 (FCM 푸시 알림)
    print("[Startup] Firebase Admin SDK 초기화...")
    PushNotificationService.initialize()

    # FAQ 챗봇 Warm-up (내부 발표용이므로 비활성화)
    # print("[Startup] FAQ 챗봇 Warm-up 백그라운드 태스크 시작...")
    # asyncio.create_task(warm_up_faq_background())


@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 리소스 정리"""
    print("[Shutdown] HTTP 클라이언트 정리 중...")
    await review_generator.close()
    print("[Shutdown] 정리 완료")


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


@app.post("/api/review/generate/stream", tags=["Review"])
async def generate_review_stream(request: ReviewRequest):
    """
    수업 리뷰 문자 메시지 스트리밍 생성

    실시간으로 생성되는 텍스트를 Server-Sent Events 형식으로 반환합니다.

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

    async def event_generator():
        """SSE 형식으로 스트리밍"""
        try:
            async for chunk in review_generator.generate_review_stream(
                student_name=request.student_name,
                parent_name=request.parent_name or request.student_name,
                learning_content=request.learning_content,
                attitude=request.attitude
            ):
                yield f"data: {chunk}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
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
