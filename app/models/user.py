from sqlalchemy import Column, BigInteger, String
from app.database.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, index=True)  # 사용자 이름
    email = Column(String, unique=True, index=True)  # 사용자 이메일
    hashed_password = Column(String)                    # 해시된 비밀번호
    role = Column(String, default="user")               # 사용자 권한 ("user" 또는 "admin")

    # 관계 설정: 한 사용자가 여러 예약을 가질 수 있음
    reservations = relationship("Reservation", back_populates="user", cascade="all, delete-orphan")