# app/api/routes/reservation.py
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.reservation import Reservation
from app.models.exam_schedule import ExamSchedule
from app.models.user import User
from app.schemas.reservation_schema import ReservationCreate, ReservationOut
from app.database.dependencies import get_db
from app.core.security import get_current_user
from app.core.exceptions import ReservationTimeError, ReservationCapacityError
from typing import List  # List 타입 추가

router = APIRouter(prefix="/reservations", tags=["reservations"])

@router.post("/", response_model=List[ReservationOut])
async def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    예약 신청 API: 특정 날짜(start_date)의 특정 시간(start_hour) ~ 특정 날짜(end_date)의 특정 시간(end_hour)에 예약 요청
    """
    # 1. 날짜 변환 및 검증
    try:
        start_date = reservation.start_date
        end_date = reservation.end_date

    except ValueError:
        raise HTTPException(status_code=400, detail="잘못된 날짜 형식입니다. YYYY-MM-DD 형식으로 입력해주세요.")

    # 2. 시험 시작 3일 전인지 체크
    if start_date - timedelta(days=3) < datetime.utcnow().date():
        raise ReservationTimeError()

    # 3. 신청 시간이 1시간 단위인지 체크
    if reservation.start_hour < 0 or reservation.end_hour > 24:
        raise HTTPException(status_code=400, detail="예약 시간 범위가 잘못되었습니다.")

    if start_date == end_date and reservation.start_hour >= reservation.end_hour:
        raise HTTPException(status_code=400, detail="같은 날짜에서 start_hour가 end_hour보다 커야 합니다.")

    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date는 end_date보다 앞서야 합니다.")

    new_reservations = []

    current_date = start_date
    current_start_hour = reservation.start_hour

    while current_date <= end_date:
        current_end_hour = 24 if current_date < end_date else reservation.end_hour  # 마지막 날짜에는 end_hour 사용

        # 해당 날짜 시간대 예약 가능 인원 체크
        confirmed_reservations = (
            db.query(Reservation)
            .filter(
                Reservation.date == current_date,
                Reservation.start_hour >= current_start_hour,
                Reservation.end_hour <= current_end_hour,
                Reservation.is_confirmed == True
            )
            .with_entities(Reservation.reserved_count)
            .all()
        )
        total_reserved = sum([r[0] for r in confirmed_reservations])

        if total_reserved + reservation.reserved_count > 50000:
            raise ReservationCapacityError()

        # 예약 생성
        new_reservation = Reservation(
            user_id=current_user.id,
            date=current_date,
            start_hour=current_start_hour,
            end_hour=current_end_hour,
            reserved_count=reservation.reserved_count,
            is_confirmed=False
        )

        db.add(new_reservation)
        db.commit()
        db.refresh(new_reservation)
        new_reservations.append(new_reservation)

        # 다음 날짜로 이동
        current_date += timedelta(days=1)
        current_start_hour = 0  # 다음 날부터는 00시부터 시작

    return new_reservations
