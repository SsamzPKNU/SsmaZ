#!/usr/bin/env python3
"""
수업 리뷰 생성 API 테스트 스크립트
"""

import requests
import json
from typing import Dict, Any


class ReviewAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    def test_health(self) -> Dict[str, Any]:
        """헬스 체크 테스트"""
        print("\n🔍 [테스트 1] 헬스 체크")
        print("-" * 50)
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            result = response.json()
            
            print(f"상태 코드: {response.status_code}")
            print(f"응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get("ollama_connected"):
                print("✅ Ollama 연결 성공")
            else:
                print("❌ Ollama 연결 실패")
                
            return result
            
        except requests.exceptions.ConnectionError:
            print("❌ API 서버에 연결할 수 없습니다.")
            print("서버가 실행 중인지 확인해주세요: python main.py")
            return {}
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return {}
    
    def test_generate_review(self, student_name: str, parent_name: str,
                            learning_content: str, attitude: str) -> Dict[str, Any]:
        """리뷰 생성 테스트"""
        print("\n📝 [테스트 2] 리뷰 생성")
        print("-" * 50)
        
        payload = {
            "student_name": student_name,
            "parent_name": parent_name,
            "learning_content": learning_content,
            "attitude": attitude
        }
        
        print(f"요청 데이터:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("\n⏳ 리뷰 생성 중... (약 10-30초 소요)")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/review/generate",
                json=payload,
                timeout=60
            )
            result = response.json()
            
            print(f"\n상태 코드: {response.status_code}")
            
            if result.get("success"):
                print("\n✅ 리뷰 생성 성공!")
                print("\n📨 생성된 메시지:")
                print("=" * 50)
                print(result.get("message"))
                print("=" * 50)
            else:
                print(f"❌ 리뷰 생성 실패: {result.get('error')}")
                
            return result
            
        except requests.exceptions.Timeout:
            print("❌ 요청 시간 초과 (60초)")
            return {}
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return {}
    
    def test_sample(self) -> Dict[str, Any]:
        """샘플 데이터로 테스트"""
        print("\n🧪 [테스트 3] 샘플 리뷰 생성")
        print("-" * 50)
        
        try:
            response = requests.get(f"{self.base_url}/api/review/test", timeout=60)
            result = response.json()
            
            print(f"상태 코드: {response.status_code}")
            
            if result.get("success"):
                print("\n✅ 샘플 리뷰 생성 성공!")
                print("\n📨 생성된 메시지:")
                print("=" * 50)
                print(result.get("message"))
                print("=" * 50)
            else:
                print(f"❌ 샘플 리뷰 생성 실패: {result.get('error')}")
                
            return result
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return {}


def main():
    print("=" * 50)
    print("🎓 학원 수업 리뷰 생성 API 테스트")
    print("=" * 50)
    
    tester = ReviewAPITester()
    
    # 1. 헬스 체크
    health_result = tester.test_health()
    
    if not health_result.get("ollama_connected"):
        print("\n⚠️  Ollama 서버가 연결되지 않았습니다.")
        print("다음을 확인해주세요:")
        print("1. Ollama 서버 실행: ollama serve")
        print("2. 모델 생성: ollama create student-review -f Modelfile")
        return
    
    # 2. 커스텀 리뷰 생성
    print("\n" + "=" * 50)
    tester.test_generate_review(
        student_name="이지훈",
        parent_name="이지훈",
        learning_content="수학 - 이차방정식 풀이 방법을 배웠습니다",
        attitude="어려운 문제도 포기하지 않고 끝까지 풀려고 노력했습니다"
    )
    
    # 3. 샘플 테스트
    print("\n" + "=" * 50)
    tester.test_sample()
    
    print("\n" + "=" * 50)
    print("✅ 모든 테스트 완료!")
    print("=" * 50)
    print("\n📚 API 문서: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
