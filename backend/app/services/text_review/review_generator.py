import httpx
import json
from typing import Dict, Any


class ReviewGenerator:
    """Ollama를 사용한 수업 리뷰 생성기"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "student-review"):
        """
        Args:
            ollama_url: Ollama 서버 URL
            model_name: 사용할 모델 이름 (Modelfile로 생성한 모델명)
        """
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.api_endpoint = f"{ollama_url}/api/generate"
        
    async def check_connection(self) -> bool:
        """Ollama 서버 연결 확인"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            print(f"Ollama 연결 실패: {e}")
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
                "stream": False  # 스트리밍 비활성화
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
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
                
        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "",
                "error": "요청 시간 초과 (60초)"
            }
        except Exception as e:
            return {
                "success": False,
                "message": "",
                "error": f"리뷰 생성 중 오류 발생: {str(e)}"
            }
