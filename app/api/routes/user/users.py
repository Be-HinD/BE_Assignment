# app/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import pwd_context  # 위에서 설정한 CryptContext
from app.models.user import User as UserModel
from app.schemas.user_schema import UserCreate, UserOut
from app.database.dependencies import get_db  # DB 세션 의존성 함수 (get_db는 SessionLocal을 yield 하는 함수)

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserOut)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # 이미 등록된 사용자인지 확인
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 비밀번호 해싱
    hashed_password = pwd_context.hash(user.password)
    # 새로운 사용자 생성
    new_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    
    # DB에 저장
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
