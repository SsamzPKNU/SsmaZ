"""
FAQ 데이터 로더
서버 시작 시 FAQ 데이터를 ChromaDB에 로드합니다.
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class FAQLoader:
    """FAQ 데이터를 ChromaDB에 로드하는 클래스"""

    def __init__(
        self,
        chromadb_host: str = "192.168.0.2",
        chromadb_port: int = 18000,
        collection_name: str = "academy_faq"
    ):
        self.chromadb_host = chromadb_host
        self.chromadb_port = chromadb_port
        self.collection_name = collection_name
        self.embedding_model: Optional[SentenceTransformer] = None
        self.chroma_client: Optional[chromadb.HttpClient] = None

    def _get_embedding_model(self) -> SentenceTransformer:
        """임베딩 모델 반환 (lazy initialization)"""
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer("snunlp/KR-SBERT-V40K-klueNLI-augSTS")
        return self.embedding_model

    def _get_chroma_client(self) -> chromadb.HttpClient:
        """ChromaDB 클라이언트 반환 (lazy initialization)"""
        if self.chroma_client is None:
            self.chroma_client = chromadb.HttpClient(
                host=self.chromadb_host,
                port=self.chromadb_port
            )
        return self.chroma_client

    def load_faq_from_json(self, json_path: str) -> List[Dict[str, Any]]:
        """JSON 파일에서 FAQ 데이터 로드"""
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def check_collection_exists(self) -> bool:
        """컬렉션에 데이터가 있는지 확인"""
        try:
            client = self._get_chroma_client()
            collection = client.get_or_create_collection(name=self.collection_name)
            count = collection.count()
            return count > 0
        except Exception as e:
            logger.error(f"[FAQ Loader] 컬렉션 확인 실패: {e}")
            return False

    def load_faq_to_chromadb(self, faq_data: List[Dict[str, Any]], force_reload: bool = False) -> bool:
        """
        FAQ 데이터를 ChromaDB에 로드

        Args:
            faq_data: FAQ 데이터 리스트
            force_reload: True면 기존 데이터 삭제 후 다시 로드

        Returns:
            성공 여부
        """
        try:
            client = self._get_chroma_client()

            # 기존 컬렉션 삭제 후 재생성 (force_reload인 경우)
            if force_reload:
                try:
                    client.delete_collection(name=self.collection_name)
                    logger.info(f"[FAQ Loader] 기존 컬렉션 '{self.collection_name}' 삭제됨")
                except Exception:
                    pass  # 컬렉션이 없으면 무시

            collection = client.get_or_create_collection(name=self.collection_name)

            # 이미 데이터가 있으면 스킵
            if collection.count() > 0 and not force_reload:
                logger.info(f"[FAQ Loader] 컬렉션에 이미 {collection.count()}개 데이터 존재, 스킵")
                return True

            # 임베딩 모델 로드
            embedding_model = self._get_embedding_model()

            # 데이터 준비
            ids = []
            documents = []
            embeddings = []
            metadatas = []

            for faq in faq_data:
                faq_id = faq["id"]
                # 질문과 답변을 합쳐서 문서 생성
                document = f"질문: {faq['question']}\n답변: {faq['answer']}"

                ids.append(faq_id)
                documents.append(document)
                metadatas.append({
                    "category": faq["category"],
                    "question": faq["question"],
                    "answer": faq["answer"]
                })

            # 임베딩 생성
            logger.info(f"[FAQ Loader] {len(documents)}개 FAQ 임베딩 생성 중...")
            embeddings = embedding_model.encode(documents).tolist()

            # ChromaDB에 추가
            collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )

            logger.info(f"[FAQ Loader] {len(ids)}개 FAQ 데이터 로드 완료")
            return True

        except Exception as e:
            logger.error(f"[FAQ Loader] ChromaDB 로드 실패: {e}")
            return False


def load_faq_to_chromadb(force_reload: bool = False) -> bool:
    """
    서버 시작 시 호출되는 FAQ 로드 함수

    Args:
        force_reload: True면 기존 데이터 삭제 후 다시 로드

    Returns:
        성공 여부
    """
    try:
        # 환경 변수에서 설정 로드
        chromadb_host = os.getenv("CHROMADB_HOST", "192.168.0.2")
        chromadb_port = int(os.getenv("CHROMADB_PORT", "18000"))
        collection_name = os.getenv("CHROMADB_COLLECTION", "academy_faq")

        logger.info(f"[FAQ Loader] ChromaDB 연결: {chromadb_host}:{chromadb_port}")

        # FAQ JSON 파일 경로
        current_dir = Path(__file__).parent.parent
        faq_json_path = current_dir / "data" / "faq_data.json"

        if not faq_json_path.exists():
            logger.warning(f"[FAQ Loader] FAQ 파일이 없습니다: {faq_json_path}")
            return False

        # FAQLoader 인스턴스 생성
        loader = FAQLoader(
            chromadb_host=chromadb_host,
            chromadb_port=chromadb_port,
            collection_name=collection_name
        )

        # JSON에서 FAQ 로드
        faq_data = loader.load_faq_from_json(str(faq_json_path))
        logger.info(f"[FAQ Loader] {len(faq_data)}개 FAQ 데이터 로드됨")

        # ChromaDB에 저장
        return loader.load_faq_to_chromadb(faq_data, force_reload=force_reload)

    except Exception as e:
        logger.error(f"[FAQ Loader] FAQ 로드 실패: {e}")
        return False


if __name__ == "__main__":
    # 테스트용 실행
    from dotenv import load_dotenv
    load_dotenv()

    success = load_faq_to_chromadb(force_reload=True)
    logger.info(f"FAQ 로드 결과: {'성공' if success else '실패'}")
