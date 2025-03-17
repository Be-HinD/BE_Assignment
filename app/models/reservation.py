from sqlalchemy import Column, BigInteger, Integer, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base
from sqlalchemy.sql import func

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    reservation_group_id = Column(BigInteger, index=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exam_schedule_id = Column(BigInteger, ForeignKey("exam_schedules.id", ondelete="CASCADE"), nullable=True)
    date = Column(Date, nullable=False)  # 예약 날짜 (YYYY-MM-DD)
    start_hour = Column(Integer, nullable=False)  # 시작 시간 (24시간제)
    end_hour = Column(Integer, nullable=False)  # 종료 시간 (24시간제)
    reserved_count = Column(Integer, nullable=False)  # 예약 인원
    is_confirmed = Column(Boolean, default=False)  # 확정 여부
    created_at = Column(DateTime, server_default=func.now())  # 자동 생성
    updated_at = Column(DateTime, onupdate=func.now())  # 예약 변경 시 자동 갱신

    # 관계 설정
    user = relationship("User", back_populates="reservations")
    exam_schedule = relationship("ExamSchedule", back_populates="reservations")
