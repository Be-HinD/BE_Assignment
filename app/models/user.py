from sqlalchemy import Column, Integer, String
from app.database.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # 사용자 이름
    email = Column(String, unique=True, index=True)  # 사용자 이메일
    hashed_password = Column(String)                    # 해시된 비밀번호
    role = Column(String, default="user")               # 사용자 권한 ("user" 또는 "admin")
