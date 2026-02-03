"""
FAQ 챗봇 서비스
RAG(Retrieval-Augmented Generation) 패턴을 사용하는 챗봇 서비스
"""

import requests
import json
from typing import AsyncGenerator, List, Dict, Any, Optional, Generator
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os


# ========================================
# 환각 방지 및 답변 제한 설정
# ========================================

# 시스템 프롬프트: AI 역할과 제약 조건 명시
SYSTEM_PROMPT = """당신은 학원 운영을 돕는 친절하고 예의 바른 상담원입니다.
오직 [Context]로 제공된 정보만을 바탕으로 답변해주세요.

[답변 규칙]
1. 제공된 정보에 답이 없으면 "죄송합니다만, 해당 내용은 등록된 정보가 없어 안내가 어렵습니다. 학원으로 직접 문의해 주시면 자세히 안내드리겠습니다."라고 정중히 안내해주세요.
2. 절대 추측하거나 지어내지 마세요.
3. 답변은 20문장 이내, 500자 이내로 간결하게 작성해주세요.
4. 학부모님과 학생분들께 예의 바르고 따뜻한 말투로 응대해주세요."""

# Ollama 생성 파라미터 (Docker 설정 변경 불가하므로 API 호출 시 적용)
OLLAMA_OPTIONS = {
    "temperature": 0.15,     # 약간의 자연스러움 유지 (0은 너무 기계적)
    "num_predict": 500,      # 최대 토큰 수 (물리적 제한)
    "top_p": 0.9,            # 확률 분포 상위 90%에서 샘플링
    "stop": ["\n\n", "User:", "###"]  # 무한 루프 방지용 중단 토큰
}

# 후처리 설정
MAX_RESPONSE_LENGTH = 600    # 최대 응답 길이 (자)
HALLUCINATION_KEYWORDS = [   # 환각 의심 키워드
    "제 생각에는", "아마도", "추측하건대", "개인적으로",
    "일반적으로", "보통은", "probably", "I think", "maybe"
]
HALLUCINATION_WARNING = "죄송합니다만, 해당 내용에 대해서는 정확한 정보를 확인하기 어렵습니다. 학원으로 직접 문의해 주시면 자세히 안내드리겠습니다."
NO_INFO_MESSAGE = "죄송합니다만, 해당 내용은 등록된 정보가 없어 안내가 어렵습니다. 학원으로 직접 문의해 주시면 자세히 안내드리겠습니다."


class ChatService:
    """FAQ 챗봇 서비스 클래스"""

    def __init__(
        self,
        chromadb_host: str = None,
        chromadb_port: int = None,
        ollama_url: str = None,
        model_name: str = None,
        collection_name: str = None
    ):
        """
        Args:
            chromadb_host: ChromaDB 서버 호스트 (기본값: 환경변수 CHROMADB_HOST)
            chromadb_port: ChromaDB 서버 포트 (기본값: 환경변수 CHROMADB_PORT)
            ollama_url: Ollama 서버 URL (기본값: 환경변수 OLLAMA_URL)
            model_name: 사용할 LLM 모델 이름 (기본값: 환경변수 CHAT_MODEL_NAME)
            collection_name: ChromaDB 컬렉션 이름 (기본값: 환경변수 CHROMADB_COLLECTION)
        """
        self.chromadb_host = chromadb_host or os.getenv("CHROMADB_HOST", "localhost")
        self.chromadb_port = chromadb_port or int(os.getenv("CHROMADB_PORT", "8000"))
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model_name = model_name or os.getenv("CHAT_MODEL_NAME", "llama31")
        self.collection_name = collection_name or os.getenv("CHROMADB_COLLECTION", "academy_faq")

        # Embedding 모델 초기화
        self.embedding_model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")

        # ChromaDB 클라이언트 초기화
        self.chroma_client: Optional[chromadb.HttpClient] = None

    def _get_chroma_client(self) -> chromadb.HttpClient:
        """ChromaDB 클라이언트 반환 (lazy initialization)"""
        if self.chroma_client is None:
            self.chroma_client = chromadb.HttpClient(
                host=self.chromadb_host,
                port=self.chromadb_port
            )
        return self.chroma_client

    def check_chromadb_connection(self) -> bool:
        """ChromaDB 연결 확인"""
        try:
            client = self._get_chroma_client()
            client.heartbeat()
            return True
        except Exception as e:
            print(f"ChromaDB 연결 실패: {e}")
            return False

    def check_ollama_connection(self) -> bool:
        """Ollama 서버 연결 확인 (requests 사용)"""
        import logging
        logger = logging.getLogger(__name__)

        try:
            url = f"{self.ollama_url}/api/tags"
            logger.info(f"Ollama 연결 시도: {url}")
            print(f"[DEBUG] Ollama 연결 시도: {url}", flush=True)
            response = requests.get(url, timeout=30)
            logger.info(f"Ollama 응답: {response.status_code}")
            print(f"[DEBUG] Ollama 응답: {response.status_code}", flush=True)
            return response.status_code == 200
        except requests.exceptions.Timeout as e:
            logger.error(f"Ollama 타임아웃: {self.ollama_url} - {e}")
            print(f"[DEBUG] Ollama 타임아웃: {self.ollama_url} - {e}", flush=True)
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ollama 연결 오류: {self.ollama_url} - {e}")
            print(f"[DEBUG] Ollama 연결 오류: {self.ollama_url} - {e}", flush=True)
            return False
        except Exception as e:
            logger.error(f"Ollama 예외: {type(e).__name__}: {e}")
            print(f"[DEBUG] Ollama 예외: {type(e).__name__}: {e}", flush=True)
            return False

    def retrieve_context(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        ChromaDB에서 유사 문서 검색

        Args:
            question: 사용자 질문
            top_k: 검색할 문서 수

        Returns:
            검색된 문서 리스트
        """
        try:
            client = self._get_chroma_client()
            collection = client.get_collection(name=self.collection_name)

            # 질문을 임베딩으로 변환
            query_embedding = self.embedding_model.encode(question).tolist()

            # 유사 문서 검색
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )

            # 결과 정리
            documents = []
            if results and results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None
                    })

            return documents

        except Exception as e:
            print(f"문서 검색 실패: {e}")
            return []

    def build_flexible_prompt(self, question: str, contexts: List[Dict[str, Any]]) -> str:
        """
        RAG 프롬프트 생성 (기존 호환용)

        Args:
            question: 사용자 질문
            contexts: 검색된 문서 리스트

        Returns:
            생성된 프롬프트
        """
        # 컨텍스트 텍스트 구성
        context_text = ""
        if contexts:
            context_parts = []
            for i, ctx in enumerate(contexts, 1):
                context_parts.append(f"[참고 {i}]\n{ctx['content']}")
            context_text = "\n\n".join(context_parts)

        prompt = f"""당신은 학원의 친절한 상담 도우미입니다. 아래 참고 자료를 바탕으로 학부모님과 학생의 질문에 정확하고 친절하게 답변해주세요.

## 참고 자료
{context_text if context_text else "(관련 자료가 없습니다)"}

## 답변 지침
1. 참고 자료에 있는 정보를 기반으로 답변해주세요.
2. 참고 자료에 없는 내용은 "해당 정보는 직접 학원에 문의해주시면 정확한 안내를 받으실 수 있습니다."라고 안내해주세요.
3. 친절하고 공손한 어투를 사용해주세요.
4. 답변은 간결하고 명확하게 해주세요.

## 질문
{question}

## 답변"""

        return prompt

    def build_strict_prompt(self, question: str, contexts: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        환각 방지를 위한 엄격한 RAG 프롬프트 생성

        Args:
            question: 사용자 질문
            contexts: ChromaDB에서 검색된 관련 문서

        Returns:
            Ollama messages 형식 리스트
        """
        # [Context] 섹션 구성
        if contexts:
            context_parts = []
            for i, ctx in enumerate(contexts, 1):
                metadata = ctx.get("metadata", {})
                q = metadata.get("question", "")
                a = metadata.get("answer", "")
                if q and a:
                    context_parts.append(f"Q{i}: {q}\nA{i}: {a}")
                else:
                    context_parts.append(f"[참고 {i}]\n{ctx['content']}")
            context_text = "\n\n".join(context_parts)
        else:
            context_text = "(관련 정보 없음)"

        user_message = f"""[Context]
{context_text}

[학부모님/학생 질문]
{question}

[상담원 답변]"""

        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]

    def _detect_hallucination(self, text: str) -> bool:
        """환각 의심 키워드 포함 여부 확인"""
        text_lower = text.lower()
        for keyword in HALLUCINATION_KEYWORDS:
            if keyword.lower() in text_lower:
                return True
        return False

    def _truncate_response(self, text: str) -> str:
        """600자 초과 시 문장 단위로 자르고 '...' 추가"""
        if len(text) <= MAX_RESPONSE_LENGTH:
            return text

        truncated = text[:MAX_RESPONSE_LENGTH]
        # 마지막 완전한 문장에서 자르기
        last_period = max(
            truncated.rfind("."),
            truncated.rfind("。"),
            truncated.rfind("!"),
            truncated.rfind("?")
        )
        if last_period > MAX_RESPONSE_LENGTH * 0.7:
            return truncated[:last_period + 1] + "..."
        return truncated + "..."

    def generate_stream_sync(self, question: str) -> Generator[str, None, None]:
        """
        환각 방지 적용된 Ollama 스트리밍 응답 생성

        흐름:
        1. ChromaDB에서 관련 문서 검색
        2. 엄격한 프롬프트 구성 (시스템 프롬프트 포함)
        3. Ollama API 호출 (temperature=0.15, num_predict=500)
        4. 실시간 후처리 (길이 제한, 환각 감지)

        Args:
            question: 사용자 질문

        Yields:
            응답 텍스트 조각
        """
        # Step 1: 관련 문서 검색
        contexts = self.retrieve_context(question, top_k=3)

        # Step 2: 검색 결과 품질 검증 (거리 0.8 이상이면 관련성 낮음)
        if not contexts or all(ctx.get("distance", 1.0) > 0.8 for ctx in contexts):
            yield NO_INFO_MESSAGE
            return

        # Step 3: 엄격한 프롬프트 생성
        messages = self.build_strict_prompt(question, contexts)

        # Step 4: Ollama API 페이로드 (options 파라미터 포함)
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            "options": OLLAMA_OPTIONS  # 환각 방지 파라미터
        }

        url = f"{self.ollama_url}/api/chat"
        full_response = []  # 후처리를 위해 전체 응답 수집

        try:
            with requests.post(url, json=payload, stream=True, timeout=120) as response:
                if response.status_code != 200:
                    yield f"[오류] Ollama API 오류: {response.status_code}"
                    return

                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode("utf-8"))
                            if "message" in data and "content" in data["message"]:
                                chunk = data["message"]["content"]
                                full_response.append(chunk)
                                current_text = "".join(full_response)

                                # 실시간 환각 감지
                                if self._detect_hallucination(current_text):
                                    yield HALLUCINATION_WARNING
                                    return

                                # 길이 초과 시 중단
                                if len(current_text) > MAX_RESPONSE_LENGTH:
                                    yield "..."
                                    return

                                yield chunk

                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue

        except requests.exceptions.Timeout:
            yield "[오류] 응답 시간 초과"
        except requests.exceptions.ConnectionError:
            yield "[오류] Ollama 서버 연결 실패"
        except Exception as e:
            yield f"[오류] 요청 실패: {str(e)}"

    async def generate_stream(self, question: str) -> AsyncGenerator[str, None]:
        """
        Ollama 스트리밍 응답 생성 (비동기 래퍼)

        Args:
            question: 사용자 질문

        Yields:
            응답 텍스트 조각
        """
        # 동기 generator를 비동기로 래핑
        for chunk in self.generate_stream_sync(question):
            yield chunk


# 싱글톤 인스턴스 생성
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """ChatService 싱글톤 인스턴스 반환"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService(
            chromadb_host=os.getenv("CHROMADB_HOST", "192.168.0.2"),
            chromadb_port=int(os.getenv("CHROMADB_PORT", "18000")),
            ollama_url=os.getenv("OLLAMA_URL", "http://192.168.0.2:11434"),
            model_name=os.getenv("CHAT_MODEL_NAME", "llama31"),
            collection_name=os.getenv("CHROMADB_COLLECTION", "academy_faq")
        )
    return _chat_service
