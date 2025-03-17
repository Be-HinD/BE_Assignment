# app/api/routes/admin_reservation.py
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.reservation import Reservation
from app.schemas.reservation_schema import ReservationGroupOut
from app.database.dependencies import get_db
from app.core.security import get_current_admin_user  # 관리자 권한 검증

router = APIRouter(prefix="/admin/reservations", tags=["admin_reservations"])

@router.get("/", response_model=List[ReservationGroupOut])
async def get_admin_reservations(
    user_id: Optional[int] = Query(None, description="특정 사용자 ID로 필터링"),
    reservation_group_id: Optional[int] = Query(None, description="특정 예약 그룹 ID로 필터링"),
    start_date: Optional[str] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD)"),
    is_confirmed: Optional[bool] = Query(None, description="확정 여부 필터"),
    past: Optional[bool] = Query(None, description="과거 예약 여부 필터"),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin_user),  # 관리자 권한 검증
):
    """
    관리자 예약 조회 API (reservation_group_id 적용)
    """
    query = db.query(Reservation)

    # 특정 사용자 ID 필터링
    if user_id:
        query = query.filter(Reservation.user_id == user_id)

    # 특정 예약 그룹 ID 필터링
    if reservation_group_id:
        query = query.filter(Reservation.reservation_group_id == reservation_group_id)

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
        now = datetime.utcnow().date()
        if past:
            query = query.filter(Reservation.date < now)
        else:
            query = query.filter(Reservation.date >= now)

    # `reservation_group_id`를 기준으로 그룹화하여 응답 데이터 구성
    reservations = query.order_by(Reservation.reservation_group_id, Reservation.date).all()

    # 응답 데이터 그룹화
    grouped_reservations = {}
    for res in reservations:
        if res.reservation_group_id not in grouped_reservations:
            grouped_reservations[res.reservation_group_id] = {
                "reservation_group_id": res.reservation_group_id,
                "user_id": res.user_id,
                "start_date": res.date,
                "end_date": res.date,  # 마지막 날짜 업데이트 예정
                "start_hour": res.start_hour,
                "end_hour": res.end_hour,
                "reserved_count": res.reserved_count,
                "is_confirmed": res.is_confirmed,
                "reservations": []
            }
        grouped_reservations[res.reservation_group_id]["end_date"] = res.date  # 마지막 날짜 업데이트
        grouped_reservations[res.reservation_group_id]["reservations"].append(res)

    # Pydantic 모델로 변환
    response_data = [
        ReservationGroupOut(**grouped_reservations[group_id]) for group_id in grouped_reservations
    ]

    return response_data
