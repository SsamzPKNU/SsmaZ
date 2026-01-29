"""
토스페이먼츠 API 클라이언트
비동기 HTTPX를 사용하여 토스페이먼츠 API와 통신
"""

import httpx
import base64
import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()


class TossPaymentClient:
    """
    토스페이먼츠 API 클라이언트
    
    주요 기능:
    - 결제 단건 조회
    - 결제 취소/환불
    - 에러 메시지 한글 변환
    """
    
    BASE_URL = "https://api.tosspayments.com/v1/payments"
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        토스페이먼츠 클라이언트 초기화
        
        Args:
            secret_key: 토스페이먼츠 시크릿 키 (없으면 환경 변수에서 로드)
        """
        self.secret_key = secret_key or os.getenv("TOSS_SECRET_KEY")
        
        if not self.secret_key:
            raise ValueError(
                "TOSS_SECRET_KEY가 설정되지 않았습니다. "
                ".env 파일에 TOSS_SECRET_KEY를 추가해주세요."
            )
        
        # Basic Auth 헤더 생성: base64(secret_key:)
        # 토스페이먼츠는 시크릿 키 뒤에 콜론(:)을 붙여서 인코딩
        auth_string = f"{self.secret_key}:"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        self.headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }
    
    async def get_payment(self, payment_key: str) -> Dict[str, Any]:
        """
        결제 단건 조회
        
        Args:
            payment_key: 토스페이먼츠 결제 키
            
        Returns:
            결제 상세 정보 (dict)
            
        Raises:
            HTTPException: API 호출 실패 시
            
        사용 예시:
            client = TossPaymentClient()
            payment = await client.get_payment("payment_key_123")
        """
        url = f"{self.BASE_URL}/{payment_key}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, timeout=10.0)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    # 에러 응답 처리
                    error_data = response.json()
                    error_message = self._translate_error_message(error_data)
                    
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=error_message
                    )
                    
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="토스페이먼츠 API 요청 시간이 초과되었습니다"
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"토스페이먼츠 API 연결에 실패했습니다: {str(e)}"
                )
    
    async def cancel_payment(
        self, 
        payment_key: str, 
        cancel_reason: str,
        cancel_amount: Optional[int] = None,
        refund_account: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        결제 취소/환불
        
        Args:
            payment_key: 토스페이먼츠 결제 키
            cancel_reason: 취소 사유
            cancel_amount: 취소 금액 (부분 취소 시, None이면 전액 취소)
            refund_account: 환불 계좌 정보 (가상계좌 환불 시 필수)
                {
                    "bank": "은행 코드",
                    "accountNumber": "계좌번호",
                    "holderName": "예금주명"
                }
                
        Returns:
            취소 결과 정보 (dict)
            
        Raises:
            HTTPException: API 호출 실패 시
            
        사용 예시:
            # 전액 취소
            result = await client.cancel_payment(
                payment_key="payment_key_123",
                cancel_reason="고객 요청"
            )
            
            # 부분 취소
            result = await client.cancel_payment(
                payment_key="payment_key_123",
                cancel_reason="부분 환불",
                cancel_amount=10000
            )
            
            # 가상계좌 환불
            result = await client.cancel_payment(
                payment_key="payment_key_123",
                cancel_reason="환불 요청",
                refund_account={
                    "bank": "88",
                    "accountNumber": "1002345678901",
                    "holderName": "홍길동"
                }
            )
        """
        url = f"{self.BASE_URL}/{payment_key}/cancel"
        
        # 요청 바디 구성
        body = {
            "cancelReason": cancel_reason
        }
        
        if cancel_amount is not None:
            body["cancelAmount"] = cancel_amount
        
        if refund_account:
            body["refundReceiveAccount"] = refund_account
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, 
                    headers=self.headers, 
                    json=body,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    # 에러 응답 처리
                    error_data = response.json()
                    error_message = self._translate_error_message(error_data)
                    
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=error_message
                    )
                    
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="토스페이먼츠 API 요청 시간이 초과되었습니다"
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"토스페이먼츠 API 연결에 실패했습니다: {str(e)}"
                )
    
    async def confirm_payment(
        self,
        payment_key: str,
        order_id: str,
        amount: int
    ) -> Dict[str, Any]:
        """
        결제 승인 요청

        토스 결제창에서 결제 완료 후 프론트에서 받은 정보로 결제를 최종 승인합니다.

        Args:
            payment_key: 토스페이먼츠 결제 키 (토스에서 발급)
            order_id: 주문 ID (우리가 생성)
            amount: 결제 금액 (검증용)

        Returns:
            결제 승인 결과 정보 (dict)

        Raises:
            HTTPException: API 호출 실패 시

        사용 예시:
            result = await client.confirm_payment(
                payment_key="tgen_202601291234567890",
                order_id="ORDER_20260129_abc123",
                amount=300000
            )
        """
        url = f"{self.BASE_URL}/confirm"

        body = {
            "paymentKey": payment_key,
            "orderId": order_id,
            "amount": amount
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=body,
                    timeout=15.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    error_data = response.json()
                    error_message = self._translate_error_message(error_data)

                    raise HTTPException(
                        status_code=response.status_code,
                        detail=error_message
                    )

            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="토스페이먼츠 API 요청 시간이 초과되었습니다"
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"토스페이먼츠 API 연결에 실패했습니다: {str(e)}"
                )

    def _translate_error_message(self, error_data: Dict[str, Any]) -> str:
        """
        토스페이먼츠 에러 코드를 한글 메시지로 변환
        
        Args:
            error_data: 토스 API 에러 응답
            
        Returns:
            한글 에러 메시지
        """
        error_code = error_data.get("code", "UNKNOWN_ERROR")
        error_message = error_data.get("message", "알 수 없는 오류가 발생했습니다")
        
        # 토스 에러 코드 -> 한글 메시지 매핑
        error_translations = {
            # 결제 조회 관련
            "NOT_FOUND_PAYMENT": "결제 정보를 찾을 수 없습니다",
            "INVALID_PAYMENT_KEY": "유효하지 않은 결제 키입니다",

            # 결제 승인 관련
            "ALREADY_PROCESSED_PAYMENT": "이미 처리된 결제입니다",
            "PROVIDER_ERROR": "결제 승인 중 오류가 발생했습니다",
            "EXCEED_MAX_CARD_INSTALLMENT_PLAN": "최대 할부 개월 수를 초과했습니다",
            "NOT_ALLOWED_POINT_USE": "포인트 사용이 허용되지 않습니다",
            "INVALID_CARD_EXPIRATION": "유효하지 않은 카드 유효기간입니다",
            "INVALID_STOPPED_CARD": "정지된 카드입니다",
            "EXCEED_MAX_DAILY_PAYMENT_COUNT": "일일 최대 결제 횟수를 초과했습니다",
            "NOT_SUPPORTED_INSTALLMENT_PLAN_CARD": "할부가 지원되지 않는 카드입니다",
            "INVALID_CARD_INSTALLMENT_PLAN": "유효하지 않은 할부 개월수입니다",
            "INVALID_CARD_NUMBER": "유효하지 않은 카드 번호입니다",
            "INVALID_AMOUNT": "결제 금액이 일치하지 않습니다",
            "NOT_FOUND_PAYMENT_SESSION": "결제 세션을 찾을 수 없습니다. 다시 시도해주세요",

            # 결제 취소 관련
            "ALREADY_CANCELED_PAYMENT": "이미 취소된 결제입니다",
            "ALREADY_REFUNDED_PAYMENT": "이미 환불된 결제입니다",
            "NOT_CANCELABLE_PAYMENT": "취소할 수 없는 결제입니다",
            "NOT_CANCELABLE_AMOUNT": "취소 가능한 금액을 초과했습니다",
            "EXCEED_CANCEL_AMOUNT_DISCOUNT_AMOUNT": "할인 금액을 초과하여 취소할 수 없습니다",
            "INVALID_REFUND_ACCOUNT": "유효하지 않은 환불 계좌입니다",
            "REFUND_ACCOUNT_NOT_FOUND": "환불 계좌 정보가 필요합니다 (가상계좌 결제)",

            # 인증 관련
            "UNAUTHORIZED_KEY": "인증되지 않은 시크릿 키입니다",
            "FORBIDDEN_REQUEST": "접근 권한이 없습니다",

            # 기타
            "INVALID_REQUEST": "잘못된 요청입니다",
            "COMMON_ERROR": "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요",
        }
        
        # 한글 메시지가 있으면 반환, 없으면 원본 메시지 반환
        translated = error_translations.get(error_code)
        
        if translated:
            return f"{translated} (코드: {error_code})"
        else:
            return f"{error_message} (코드: {error_code})"
