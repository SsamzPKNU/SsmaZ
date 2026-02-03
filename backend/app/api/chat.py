"""
FAQ 챗봇 API
RAG(Retrieval-Augmented Generation) 패턴을 사용하는 학원 FAQ 챗봇
캐싱을 통해 응답 지연 최소화
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, ChatErrorResponse
from app.services.chat_service import get_chat_service
from app.services.chat_cache import get_faq_cache
from app.api.deps import get_admin_user
from app.models.user import User


router = APIRouter(
    prefix="/api/chat",
    tags=["FAQ 챗봇"]
)


@router.post(
    "",
    summary="FAQ 챗봇 질문",
    description="학원 FAQ에 대한 질문을 받아 실시간 스트리밍으로 답변합니다.",
    responses={
        200: {
            "description": "스트리밍 응답",
            "content": {"text/event-stream": {}}
        },
        400: {"model": ChatErrorResponse, "description": "잘못된 요청"},
        503: {"model": ChatErrorResponse, "description": "서비스 연결 실패"}
    }
)
async def chat(request: ChatRequest):
    """
    FAQ 챗봇 엔드포인트

    - **question**: 질문 내용 (필수)

    StreamingResponse로 실시간 응답을 반환합니다.
    """
    # 질문 유효성 검사
    question = request.question.strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": "질문이 비어있습니다",
                "error_code": "EMPTY_QUESTION"
            }
        )

    chat_service = get_chat_service()

    # ChromaDB 연결 확인
    if not chat_service.check_chromadb_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "ChromaDB 연결에 실패했습니다. 잠시 후 다시 시도해주세요.",
                "error_code": "CHROMADB_CONNECTION_ERROR"
            }
        )

    # Ollama 연결 확인
    if not chat_service.check_ollama_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "detail": "Ollama 연결에 실패했습니다. 잠시 후 다시 시도해주세요.",
                "error_code": "OLLAMA_CONNECTION_ERROR"
            }
        )

    # 스트리밍 응답 생성
    async def generate():
        try:
            async for chunk in chat_service.generate_stream(question):
                yield chunk
        except Exception as e:
            yield f"\n[오류] 응답 생성 중 문제가 발생했습니다: {str(e)}"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/health", summary="챗봇 서비스 상태 확인")
async def chat_health():
    """
    챗봇 서비스의 ChromaDB 및 Ollama 연결 상태를 확인합니다.
    """
    chat_service = get_chat_service()
    cache = get_faq_cache()

    chromadb_connected = chat_service.check_chromadb_connection()
    ollama_connected = chat_service.check_ollama_connection()
    cache_stats = cache.get_stats()

    return {
        "status": "healthy" if (chromadb_connected and ollama_connected) else "unhealthy",
        "chromadb_connected": chromadb_connected,
        "ollama_connected": ollama_connected,
        "model_name": chat_service.model_name,
        "cache": cache_stats,
        "debug": {
            "ollama_url": chat_service.ollama_url,
            "chromadb_host": chat_service.chromadb_host,
            "chromadb_port": chat_service.chromadb_port
        }
    }


@router.get(
    "/cache/stats",
    summary="캐시 통계 조회",
    description="FAQ 챗봇 캐시의 통계 정보를 조회합니다."
)
async def get_cache_stats():
    """
    캐시 통계 조회

    - **cache_size**: 현재 캐시된 응답 수
    - **hits**: 캐시 히트 횟수
    - **misses**: 캐시 미스 횟수
    - **hit_rate**: 캐시 히트율 (%)
    """
    cache = get_faq_cache()
    return cache.get_stats()


@router.post(
    "/cache/clear",
    summary="캐시 초기화 (관리자 전용)",
    description="FAQ 챗봇 캐시를 초기화합니다. 관리자 권한이 필요합니다."
)
async def clear_cache(admin_user: User = Depends(get_admin_user)):
    """
    캐시 초기화 (관리자 전용)

    모든 캐시된 응답을 삭제합니다.
    """
    cache = get_faq_cache()
    previous_stats = cache.get_stats()
    cache.clear()

    return {
        "message": "캐시가 초기화되었습니다",
        "previous_stats": previous_stats,
        "current_stats": cache.get_stats()
    }
