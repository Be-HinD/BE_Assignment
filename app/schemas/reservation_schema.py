from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

class ReservationBase(BaseModel):
    date: date  # 날짜 타입 변경 (Pydantic이 자동 변환)
    start_hour: int  # 시작 시간 (0~23시)
    end_hour: int  # 종료 시간 (1~24시)
    reserved_count: int  # 신청 인원

class ReservationCreate(BaseModel):
    start_date: date 
    start_hour: int  # 0 ~ 23
    end_date: date
    end_hour: int  # 0 ~ 23
    reserved_count: int  # 예약 인원

    class Config:
        from_attributes = True

class ReservationOut(BaseModel):
    id: int
    reservation_group_id: int
    user_id: int
    date: date  # ✅ `str` → `date` 타입 변경
    start_hour: int
    end_hour: int
    reserved_count: int
    is_confirmed: bool
    created_at: datetime

    class Config:
        from_attributes = True 

class ReservationGroupOut(BaseModel):
    reservation_group_id: int
    user_id: int
    start_date: date
    end_date: date
    start_hour: int
    end_hour: int
    reserved_count: int
    is_confirmed: bool
    reservations: List[ReservationOut]

    class Config:
        from_attributes = True