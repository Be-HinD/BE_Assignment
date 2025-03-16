from sqlalchemy import Column, BigInteger, Integer, Boolean, Date
from sqlalchemy.orm import relationship
from app.database.base import Base

class ExamSchedule(Base):
    __tablename__ = "exam_schedules"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    date = Column(Date, nullable=False)  # 시험 날짜
    start_hour = Column(Integer, nullable=False)  # 시작 시간
    end_hour = Column(Integer, nullable=False)  # 종료 시간
    total_reserved_count = Column(Integer, nullable=False)  # 확정된 예약 인원

    # 관계 설정
    reservations = relationship("Reservation", back_populates="exam_schedule")
