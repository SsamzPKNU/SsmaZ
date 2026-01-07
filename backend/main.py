from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.text_review import ReviewRequest, ReviewResponse, HealthResponse
from app.services.text_review.review_generator import ReviewGenerator
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="학원 수업 리뷰 생성 API",
    description="강사가 학생의 수업 리뷰를 학부모에게 보낼 문자 메시지를 자동 생성합니다",
    version="1.0.0"
)

# CORS 설정 (필요시)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "message": "학원 수업 리뷰 생성 API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
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
