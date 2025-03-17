# app/api/routes/admin_reservation.py
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.exam_schedule import ExamSchedule
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

@router.post("/confirm/{reservation_group_id}")
async def confirm_reservation(
    reservation_group_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin_user),
):
    """
    관리자 예약 확정 API: reservation_group_id에 해당하는 예약을 확정하고, exam_schedules에 반영한다.
    """
    # 예약 그룹 조회
    reservations = (
        db.query(Reservation)
        .filter(Reservation.reservation_group_id == reservation_group_id, Reservation.is_confirmed == False)
        .all()
    )
    
    if not reservations:
        raise HTTPException(status_code=404, detail="해당 예약 그룹을 찾을 수 없거나 이미 확정된 예약입니다.")

    # 예약 확정 가능 여부 확인 (같은 시간대 예약 50,000명 초과 여부)
    for res in reservations:
        total_reserved = (
            db.query(func.sum(Reservation.reserved_count))
            .filter(
                Reservation.date == res.date,
                Reservation.start_hour == res.start_hour,
                Reservation.end_hour == res.end_hour,
                Reservation.is_confirmed == True,
            )
            .scalar() or 0
        )

        if total_reserved + res.reserved_count > 50000:
            raise HTTPException(
                status_code=400,
                detail=f"{res.date} {res.start_hour}:00 ~ {res.end_hour}:00 예약이 인원 초과로 확정 불가",
            )

    # 트랜잭션 처리 (예외 발생 시 롤백)
    try:
        for res in reservations:
            # `exam_schedules`에 해당 시간대의 일정이 있는지 확인
            exam_schedule = (
                db.query(ExamSchedule)
                .filter(
                    ExamSchedule.date == res.date,
                    ExamSchedule.start_hour == res.start_hour,
                    ExamSchedule.end_hour == res.end_hour,
                )
                .first()
            )

            if exam_schedule:
                # 기존 일정이 있으면 `total_reserved_count` 증가
                exam_schedule.total_reserved_count += res.reserved_count
            else:
                # 새로운 일정 생성
                exam_schedule = ExamSchedule(
                    date=res.date,
                    start_hour=res.start_hour,
                    end_hour=res.end_hour,
                    total_reserved_count=res.reserved_count,
                )
                db.add(exam_schedule)
                db.flush()  # 새로 추가된 객체의 ID를 가져오기 위해 flush 수행

            # 예약 확정 및 `exam_schedule_id` 업데이트
            res.is_confirmed = True
            res.exam_schedule_id = exam_schedule.id  # ✅ `exam_schedule_id` 갱신

        # 변경 사항 커밋
        db.commit()
        return {"message": "예약 확정 완료", "reservation_group_id": reservation_group_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"예약 확정 중 오류 발생: {str(e)}")
