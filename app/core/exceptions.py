# app/core/exceptions.py
from fastapi import HTTPException

class ReservationTimeError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="예약 신청은 시험 시작 3일 전까지 가능합니다.")

class ReservationCapacityError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="해당 시간대의 예약이 최대 수용 인원을 초과합니다.")
