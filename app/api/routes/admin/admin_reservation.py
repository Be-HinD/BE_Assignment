# app/api/routes/admin_reservation.py
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.reservation import Reservation
from app.schemas.reservation_schema import ReservationOut
from app.database.dependencies import get_db
from app.core.security import get_current_admin_user  # 관리자 권한 검증

router = APIRouter(prefix="/admin/reservations", tags=["admin_reservations"])

@router.get("/", response_model=List[ReservationOut])
async def get_admin_reservations(
    user_id: Optional[int] = Query(None, description="특정 사용자 ID로 필터링"),
    start_date: Optional[str] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD)"),
    is_confirmed: Optional[bool] = Query(None, description="확정 여부 필터"),
    past: Optional[bool] = Query(None, description="과거 예약 여부 필터"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user),  # 관리자 권한 검증
):
    """
    관리자 예약 조회 API: 모든 예약 정보를 필터링하여 조회한다.
    - 특정 사용자 예약 조회 가능 (user_id)
    - 날짜 범위 지정 가능 (start_date, end_date)
    - 확정 여부 필터링 가능 (is_confirmed)
    - 과거 또는 미래 예약 필터링 가능 (past)
    """
    query = db.query(Reservation)

    # 특정 사용자 ID 필터링
    if user_id:
        query = query.filter(Reservation.user_id == user_id)

    # 날짜 필터링
    if start_date:
        try:
            start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(Reservation.date >= start_date_parsed)
        except ValueError:
            raise HTTPException(status_code=400, detail="잘못된 날짜 형식입니다. YYYY-MM-DD 형식으로 입력해주세요.")
    
    if end_date:
        try:
            end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(Reservation.date <= end_date_parsed)
        except ValueError:
            raise HTTPException(status_code=400, detail="잘못된 날짜 형식입니다. YYYY-MM-DD 형식으로 입력해주세요.")

    # 확정 여부 필터링
    if is_confirmed is not None:
        query = query.filter(Reservation.is_confirmed == is_confirmed)

    # 과거 예약 필터링
    if past is not None:
        now = datetime.date()
        if past:
            query = query.filter(Reservation.date < now)
        else:
            query = query.filter(Reservation.date >= now)

    print("404?")
    # 데이터 조회 및 반환
    admin_reservations = query.all()
    return admin_reservations
