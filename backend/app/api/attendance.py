from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from datetime import date
from app.schemas.attendance import AttendanceCheckRequest, AttendanceResponse, TodayAttendanceResponse
from app.services.attendance_service import AttendanceService

router = APIRouter()

@router.get("/today", response_model=TodayAttendanceResponse)
def get_today_attendance(db: Session = Depends(get_db)):
    """
    오늘의 출결 현황 조회
    모든 학생 목록과 그들의 오늘 출결 상태를 반환
    """
    results = AttendanceService.get_today_attendance(db)
    return {
        "date": date.today(),
        "students": results
    }


@router.post("/check", response_model=AttendanceResponse)
def check_attendance(
    request: AttendanceCheckRequest,
    db: Session = Depends(get_db)
):
    """
    출결 체크 API
    - 등원/지각/조퇴/결석 등의 상태 변경 (action='CHECK_IN')
    - 하원 처리 (action='CHECK_OUT')
    """
    try:
        # action 처리: 'CHECK_OUT'인 경우 flag 설정
        is_checkout = False
        if request.action and request.action.upper() == "CHECK_OUT":
            is_checkout = True
            
        result = AttendanceService.check_attendance(
            db=db,
            student_id=request.student_id,
            status=request.status,
            method=request.method,
            is_checkout=is_checkout  # Service에 전달 (Service 수정 필요)
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
