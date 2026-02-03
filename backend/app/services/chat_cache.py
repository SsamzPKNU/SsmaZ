"""
FAQ 챗봇 캐싱 모듈
functools.lru_cache 기반 응답 캐싱으로 응답 지연 최소화
"""

import hashlib
import re
import threading
import time
from functools import lru_cache
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class CacheStats:
    """캐시 통계 데이터 클래스"""
    hits: int = 0
    misses: int = 0
    cache_size: int = 0

    @property
    def hit_rate(self) -> float:
        """캐시 히트율 계산"""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100


class FAQCache:
    """
    FAQ 응답 캐싱 클래스

    특징:
    - 질문 정규화로 유사 질문 통합
    - 스레드 안전 (RLock 사용)
    - 최대 100개 응답 캐싱
    - 에러 응답은 캐싱하지 않음
    """

    # 캐시 설정
    CACHE_MAXSIZE = 100  # FAQ 20개 + 변형 질문 80개

    def __init__(self):
        self._lock = threading.RLock()
        self._stats = CacheStats()
        self._cache: Dict[str, Tuple[str, float]] = {}  # hash -> (response, timestamp)
        self._context_cache: Dict[str, Any] = {}  # hash -> context (검색 결과)

    def normalize_question(self, question: str) -> str:
        """
        질문 정규화
        - 소문자 변환
        - 연속 공백 제거
        - 특수문자 제거 (한글, 영문, 숫자, 공백 유지)
        - 앞뒤 공백 제거

        Args:
            question: 원본 질문

        Returns:
            정규화된 질문
        """
        # 소문자 변환
        normalized = question.lower()

        # 특수문자 제거 (한글, 영문, 숫자, 공백만 유지)
        normalized = re.sub(r'[^\w\s가-힣]', '', normalized)

        # 연속 공백을 단일 공백으로
        normalized = re.sub(r'\s+', ' ', normalized)

        # 앞뒤 공백 제거
        normalized = normalized.strip()

        return normalized

    def get_question_hash(self, question: str) -> str:
        """
        정규화된 질문의 MD5 해시 생성

        Args:
            question: 원본 질문

        Returns:
            해시 문자열
        """
        normalized = self.normalize_question(question)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()

    def get_cached_response(self, question: str) -> Optional[str]:
        """
        캐시된 응답 조회

        Args:
            question: 사용자 질문

        Returns:
            캐시된 응답 또는 None
        """
        question_hash = self.get_question_hash(question)

        with self._lock:
            if question_hash in self._cache:
                self._stats.hits += 1
                response, _ = self._cache[question_hash]
                return response

            self._stats.misses += 1
            return None

    def cache_response(self, question: str, response: str) -> None:
        """
        응답 캐싱

        에러 응답([오류]로 시작)은 캐싱하지 않음

        Args:
            question: 사용자 질문
            response: 생성된 응답
        """
        # 에러 응답은 캐싱하지 않음
        if response.startswith("[오류]"):
            return

        question_hash = self.get_question_hash(question)

        with self._lock:
            # 캐시 크기 제한 (LRU 방식)
            if len(self._cache) >= self.CACHE_MAXSIZE:
                # 가장 오래된 항목 제거
                oldest_hash = min(self._cache, key=lambda k: self._cache[k][1])
                del self._cache[oldest_hash]
                if oldest_hash in self._context_cache:
                    del self._context_cache[oldest_hash]

            self._cache[question_hash] = (response, time.time())
            self._stats.cache_size = len(self._cache)

    def get_cached_context(self, question: str) -> Optional[Any]:
        """
        캐시된 검색 컨텍스트 조회 (ChromaDB 검색 결과)

        Args:
            question: 사용자 질문

        Returns:
            캐시된 컨텍스트 또는 None
        """
        question_hash = self.get_question_hash(question)

        with self._lock:
            return self._context_cache.get(question_hash)

    def cache_context(self, question: str, context: Any) -> None:
        """
        검색 컨텍스트 캐싱

        Args:
            question: 사용자 질문
            context: ChromaDB 검색 결과
        """
        question_hash = self.get_question_hash(question)

        with self._lock:
            self._context_cache[question_hash] = context

    def get_stats(self) -> Dict[str, Any]:
        """
        캐시 통계 반환

        Returns:
            통계 딕셔너리 (cache_size, hits, misses, hit_rate)
        """
        with self._lock:
            return {
                "cache_size": self._stats.cache_size,
                "hits": self._stats.hits,
                "misses": self._stats.misses,
                "hit_rate": f"{self._stats.hit_rate:.1f}%"
            }

    def clear(self) -> None:
        """캐시 초기화"""
        with self._lock:
            self._cache.clear()
            self._context_cache.clear()
            self._stats = CacheStats()

    def is_warmed_up(self) -> bool:
        """Warm-up 완료 여부 확인"""
        with self._lock:
            return self._stats.cache_size > 0


# 싱글톤 인스턴스
_faq_cache: Optional[FAQCache] = None


def get_faq_cache() -> FAQCache:
    """FAQCache 싱글톤 인스턴스 반환"""
    global _faq_cache
    if _faq_cache is None:
        _faq_cache = FAQCache()
    return _faq_cache
