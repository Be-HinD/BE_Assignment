# app/api/routes/reservation.py
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.reservation import Reservation
from app.models.exam_schedule import ExamSchedule
from app.models.user import User
from app.schemas.reservation_schema import ReservationCreate, ReservationOut, ReservationUpdate
from app.database.dependencies import get_db
from app.core.security import get_current_user
from app.core.exceptions import ReservationTimeError, ReservationCapacityError
from typing import List, Optional  # List 타입 추가

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("/", response_model=List[dict])
async def get_user_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    date: str = None,
    is_confirmed: bool = None,
    past: bool = None,
):
    """
    사용자의 예약 조회 API (예약 그룹별로 묶어서 반환)
    """
    query = db.query(Reservation).filter(Reservation.user_id == current_user.id)

    if date:
        try:
            query_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(Reservation.date == query_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="잘못된 날짜 형식입니다.")

    if is_confirmed is not None:
        query = query.filter(Reservation.is_confirmed == is_confirmed)

    if past is not None:
        now = datetime.utcnow().date()
        if past:
            query = query.filter(Reservation.date < now)
        else:
            query = query.filter(Reservation.date >= now)

    reservations = query.all()
    
    grouped_reservations = {}
    for r in reservations:
        if r.reservation_group_id not in grouped_reservations:
            grouped_reservations[r.reservation_group_id] = {
                "reservation_group_id": r.reservation_group_id,
                "reservations": []
            }
        grouped_reservations[r.reservation_group_id]["reservations"].append({
            "reservation_id": r.id,
            "date": r.date.strftime("%Y-%m-%d"),
            "start_hour": r.start_hour,
            "end_hour": r.end_hour,
            "reserved_count": r.reserved_count,
            "is_confirmed": r.is_confirmed
        })

    return list(grouped_reservations.values())


@router.post("/", response_model=List[ReservationOut])
async def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    예약 신청 API: 특정 날짜(start_date)의 특정 시간(start_hour) ~ 특정 날짜(end_date)의 특정 시간(end_hour)에 예약 요청
    """

    new_group_id = db.query(func.coalesce(func.max(Reservation.reservation_group_id), 0) + 1).scalar()

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
            reservation_group_id=new_group_id,
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

@router.put("/{reservation_group_id}")
async def update_reservation(
    reservation_group_id: int,
    updated_reservation: ReservationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    사용자 본인 예약 수정 API:
    - 예약이 본인 예약인지 확인
    - 예약이 확정되지 않았는지 확인
    - 예약 시작 시간이 현재 시간 기준 3일 이전인지 확인
    - 기존 예약 데이터를 삭제 후 새로운 예약 데이터 삽입
    """

    # 기존 예약 조회 (reservation_group_id 기반)
    reservations = (
        db.query(Reservation)
        .filter(
            Reservation.reservation_group_id == reservation_group_id,
            Reservation.user_id == current_user.id,
        )
        .all()
    )

    if not reservations:
        raise HTTPException(status_code=404, detail="해당 예약이 존재하지 않거나 수정 권한이 없습니다.")

    # 확정 여부 확인
    if any(res.is_confirmed for res in reservations):
        raise HTTPException(status_code=400, detail="확정된 예약은 수정할 수 없습니다.")

    # 예약 시작 시간이 현재 기준 3일 이내인지 확인
    start_date = min(res.date for res in reservations)  # 기존 예약 중 가장 빠른 날짜
    if start_date - timedelta(days=3) < datetime.utcnow().date():
        raise HTTPException(status_code=400, detail="예약 시작 시간이 3일 이내인 경우 수정할 수 없습니다.")

    # 트랜잭션 처리 (삭제 후 신규 데이터 삽입)
    try:
        db.query(Reservation).filter(Reservation.reservation_group_id == reservation_group_id).delete()

        new_reservations = []
        current_date = updated_reservation.start_date
        current_start_hour = updated_reservation.start_hour

        while current_date <= updated_reservation.end_date:
            current_end_hour = 24 if current_date < updated_reservation.end_date else updated_reservation.end_hour

            new_reservation = Reservation(
                reservation_group_id=reservation_group_id,
                user_id=current_user.id,
                date=current_date,
                start_hour=current_start_hour,
                end_hour=current_end_hour,
                reserved_count=updated_reservation.reserved_count,
                is_confirmed=False,
            )

            db.add(new_reservation)
            new_reservations.append(new_reservation)

            current_date += timedelta(days=1)
            current_start_hour = 0  # 다음 날짜부터는 00시부터 시작

        db.commit()
        return {"message": "예약 수정 완료", "reservation_group_id": reservation_group_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"예약 수정 중 오류 발생: {str(e)}")
    
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.reservation import Reservation
from app.database.dependencies import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/reservations", tags=["reservations"])

@router.delete("/{reservation_group_id}")
async def delete_reservation(
    reservation_group_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    사용자의 예약 삭제 API
    - 본인 예약인지 확인
    - 확정되지 않은 예약만 삭제 가능
    """
    # 해당 `reservation_group_id`에 속하는 예약 조회
    reservations = (
        db.query(Reservation)
        .filter(Reservation.reservation_group_id == reservation_group_id)
        .all()
    )

    if not reservations:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다.")

    # 본인 예약인지 확인
    if reservations[0].user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인의 예약만 삭제할 수 있습니다.")

    # 확정된 예약인지 확인
    for res in reservations:
        if res.is_confirmed:
            raise HTTPException(status_code=400, detail="확정된 예약은 삭제할 수 없습니다.")

    # 트랜잭션을 사용하여 예약 삭제
    try:
        for res in reservations:
            db.delete(res)
        db.commit()
        return {"message": "예약이 성공적으로 삭제되었습니다.", "reservation_group_id": reservation_group_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"예약 삭제 중 오류 발생: {str(e)}")
