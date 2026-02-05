import os
import json
import httpx
import logging
from typing import Dict, Any, AsyncGenerator, Optional

logger = logging.getLogger(__name__)


class ReviewGenerator:
    """Ollama를 사용한 수업 리뷰 생성기"""

    # 모델 메모리 유지 시간 (30분)
    DEFAULT_KEEP_ALIVE = "30m"

    def __init__(self, ollama_url: str = None, model_name: str = None):
        """
        Args:
            ollama_url: Ollama 서버 URL (기본값: 환경변수 OLLAMA_URL)
            model_name: 사용할 모델 이름 (기본값: 환경변수 MODEL_NAME)
        """
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model_name = model_name or os.getenv("MODEL_NAME", "llama31:latest")
        self.api_endpoint = f"{self.ollama_url}/api/generate"

        # HTTP 클라이언트 싱글톤 (Connection Pool 재사용)
        self._client: Optional[httpx.AsyncClient] = None
        self._is_warmed_up = False

        logger.info(f"ReviewGenerator 초기화: {self.ollama_url}")

    async def get_client(self) -> httpx.AsyncClient:
        """HTTP 클라이언트 싱글톤 반환 (Keep-alive 연결 재사용)"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(120.0, connect=10.0),
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._client

    async def close(self):
        """클라이언트 정리 (앱 종료 시 호출)"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            logger.info("HTTP 클라이언트 정리 완료")

    async def warm_up(self) -> bool:
        """
        서버 시작 시 모델 미리 로드 (Warm-up)
        빈 프롬프트로 모델을 메모리에 로드
        """
        try:
            logger.info(f"Ollama 모델 Warm-up 시작: {self.model_name}")

            client = await self.get_client()
            payload = {
                "model": self.model_name,
                "prompt": "",
                "keep_alive": self.DEFAULT_KEEP_ALIVE,
                "stream": False
            }

            response = await client.post(self.api_endpoint, json=payload)

            if response.status_code == 200:
                self._is_warmed_up = True
                logger.info(f"Ollama 모델 Warm-up 완료: {self.model_name}")
                return True
            else:
                logger.warning(f"Warm-up 실패: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Warm-up 중 오류: {e}")
            return False

    @property
    def is_ready(self) -> bool:
        """모델이 준비되었는지 확인"""
        return self._is_warmed_up

    async def check_connection(self) -> bool:
        """Ollama 서버 연결 확인"""
        try:
            client = await self.get_client()
            response = await client.get(f"{self.ollama_url}/api/tags")
            return response.status_code == 200
        except httpx.ConnectError as e:
            logger.error(f"Ollama 연결 거부: {self.ollama_url} - {e}")
            return False
        except httpx.TimeoutException as e:
            logger.error(f"Ollama 타임아웃: {e}")
            return False
        except Exception as e:
            logger.error(f"Ollama 연결 실패: {e}")
            return False
    
    def _create_prompt(self, student_name: str, parent_name: str, 
                       learning_content: str, attitude: str) -> str:
        """프롬프트 생성"""
        # parent_name이 없으면 student_name 사용
        parent_display_name = parent_name if parent_name else student_name
        
        prompt = f"""다음 정보를 바탕으로 학부모님께 보낼 문자 메시지를 작성해줘:

[학생 정보]
- 학생 이름: {student_name}
- 학부모 호칭: {parent_display_name} 어머님

[수업 내용]
- 학습내용: {learning_content}
- 태도: {attitude}

위 정보를 바탕으로 따뜻하고 정성스러운 피드백 문자를 작성해줘."""
        
        return prompt
    
    async def generate_review(self, student_name: str, parent_name: str,
                             learning_content: str, attitude: str) -> Dict[str, Any]:
        """
        수업 리뷰 문자 메시지 생성

        Returns:
            Dict: {"success": bool, "message": str, "error": str}
        """
        try:
            prompt = self._create_prompt(student_name, parent_name, learning_content, attitude)

            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "keep_alive": self.DEFAULT_KEEP_ALIVE
            }

            client = await self.get_client()
            response = await client.post(self.api_endpoint, json=payload)

            if response.status_code != 200:
                return {
                    "success": False,
                    "message": "",
                    "error": f"Ollama API 오류: {response.status_code}"
                }

            result = response.json()
            generated_text = result.get("response", "").strip()

            if not generated_text:
                return {
                    "success": False,
                    "message": "",
                    "error": "생성된 메시지가 비어있습니다"
                }

            return {
                "success": True,
                "message": generated_text,
                "error": None
            }

        except httpx.ConnectError as e:
            logger.error(f"Ollama 서버 연결 거부: {self.ollama_url} - {e}")
            return {
                "success": False,
                "message": "",
                "error": f"Ollama 서버 연결 거부: {self.ollama_url}"
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "",
                "error": "요청 시간 초과 (60초)"
            }
        except Exception as e:
            logger.error(f"리뷰 생성 중 오류: {e}")
            return {
                "success": False,
                "message": "",
                "error": f"리뷰 생성 중 오류 발생: {str(e)}"
            }

    async def generate_review_stream(
        self,
        student_name: str,
        parent_name: str,
        learning_content: str,
        attitude: str
    ) -> AsyncGenerator[str, None]:
        """
        스트리밍 방식으로 리뷰 생성

        Yields:
            str: 생성된 텍스트 조각
        """
        try:
            prompt = self._create_prompt(student_name, parent_name, learning_content, attitude)

            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": True,
                "keep_alive": self.DEFAULT_KEEP_ALIVE
            }

            client = await self.get_client()

            async with client.stream("POST", self.api_endpoint, json=payload) as response:
                if response.status_code != 200:
                    yield f"[ERROR] Ollama API 오류: {response.status_code}"
                    return

                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)

                            if "response" in data:
                                yield data["response"]

                            if data.get("done", False):
                                break

                        except json.JSONDecodeError:
                            continue

        except httpx.ConnectError as e:
            logger.error(f"Ollama 서버 연결 거부: {e}")
            yield "[ERROR] Ollama 서버 연결 실패"
        except httpx.TimeoutException:
            yield "[ERROR] 요청 시간 초과"
        except Exception as e:
            logger.error(f"스트리밍 중 오류: {e}")
            yield f"[ERROR] {str(e)}"
