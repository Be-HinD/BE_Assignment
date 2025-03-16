from sqlalchemy import Column, BigInteger, Integer, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base
from sqlalchemy.sql import func

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # ✅ ForeignKey 추가
    exam_schedule_id = Column(BigInteger, ForeignKey("exam_schedules.id", ondelete="CASCADE"), nullable=True)  # ✅ ForeignKey 추가
    date = Column(Date, nullable=False)  # 예약 날짜 (YYYY-MM-DD)
    start_hour = Column(Integer, nullable=False)  # 시작 시간 (24시간제)
    end_hour = Column(Integer, nullable=False)  # 종료 시간 (24시간제)
    reserved_count = Column(Integer, nullable=False)  # 예약 인원
    is_confirmed = Column(Boolean, default=False)  # 확정 여부
    created_at = Column(DateTime, server_default=func.now())  # 자동 생성

    # 관계 설정
    user = relationship("User", back_populates="reservations")
    exam_schedule = relationship("ExamSchedule", back_populates="reservations")
