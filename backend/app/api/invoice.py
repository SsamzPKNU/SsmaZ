"""
Invoice API 라우터
청구서 관련 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_admin_user
from app.models.user import User
from app.schemas.invoice import (
    InvoiceCreate, InvoiceBulkCreate, InvoiceSendRequest, InvoiceMarkPaidRequest,
    InvoiceResponse, InvoiceListResponse, InvoiceBulkCreateResponse, InvoiceSendResponse
)
from app.services.invoice_service import InvoiceService

router = APIRouter(
    prefix="/api/admin/invoices",
    tags=["청구서 관리"]
)


@router.get("", response_model=InvoiceListResponse)
async def get_invoices(
    status: Optional[str] = Query(None, description="상태 필터 (PENDING, SENT, PAID, OVERDUE, CANCELLED)"),
    student_id: Optional[int] = Query(None, description="학생 ID 필터"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """청구서 목록 조회 (관리자 전용)"""
    invoices, total = InvoiceService.get_invoices(
        db=db,
        academy_id=admin_user.academy_id,
        status=status,
        student_id=student_id,
        skip=skip,
        limit=limit
    )
    return InvoiceListResponse(
        total=total,
        invoices=[InvoiceService.to_response(i) for i in invoices]
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """청구서 상세 조회 (관리자 전용)"""
    invoice = InvoiceService.get_invoice(db, invoice_id, admin_user.academy_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="청구서를 찾을 수 없습니다"
        )
    return InvoiceService.to_response(invoice)


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    data: InvoiceCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """청구서 단건 생성 (관리자 전용)"""
    try:
        invoice = InvoiceService.create_invoice(
            db=db,
            academy_id=admin_user.academy_id,
            data=data
        )
        return InvoiceService.to_response(invoice)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/bulk", response_model=InvoiceBulkCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_invoices_bulk(
    data: InvoiceBulkCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """청구서 일괄 생성 (관리자 전용)"""
    invoices = InvoiceService.create_invoices_bulk(
        db=db,
        academy_id=admin_user.academy_id,
        data=data
    )
    return InvoiceBulkCreateResponse(
        success_count=len(invoices),
        invoices=[InvoiceService.to_response(i) for i in invoices]
    )


@router.post("/send", response_model=InvoiceSendResponse)
async def send_invoices(
    data: InvoiceSendRequest,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """청구서 발송 (관리자 전용)"""
    sent_count, failed_ids = InvoiceService.send_invoices(
        db=db,
        academy_id=admin_user.academy_id,
        invoice_ids=data.invoice_ids
    )
    return InvoiceSendResponse(
        sent_count=sent_count,
        failed_count=len(failed_ids),
        failed_ids=failed_ids
    )


@router.put("/{invoice_id}/paid", response_model=InvoiceResponse)
async def mark_invoice_paid(
    invoice_id: int,
    data: InvoiceMarkPaidRequest = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """청구서 납부 완료 처리 (관리자 전용)"""
    try:
        payment_id = data.payment_id if data else None
        invoice = InvoiceService.mark_as_paid(
            db=db,
            invoice_id=invoice_id,
            academy_id=admin_user.academy_id,
            payment_id=payment_id
        )
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="청구서를 찾을 수 없습니다"
            )
        return InvoiceService.to_response(invoice)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{invoice_id}", response_model=InvoiceResponse)
async def cancel_invoice(
    invoice_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """청구서 취소 (관리자 전용)"""
    try:
        invoice = InvoiceService.cancel_invoice(
            db=db,
            invoice_id=invoice_id,
            academy_id=admin_user.academy_id
        )
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="청구서를 찾을 수 없습니다"
            )
        return InvoiceService.to_response(invoice)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/check-overdue")
async def check_overdue_invoices(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """연체 청구서 상태 업데이트 (관리자 전용)"""
    updated_count = InvoiceService.check_overdue_invoices(
        db=db,
        academy_id=admin_user.academy_id
    )
    return {"updated_count": updated_count, "message": f"{updated_count}건의 청구서가 연체 상태로 변경되었습니다"}
