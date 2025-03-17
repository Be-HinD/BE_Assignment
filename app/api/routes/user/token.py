from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.security import create_access_token, pwd_context
from app.core.config import settings
from app.database.dependencies import get_db
from app.models.user import User as UserModel

router = APIRouter(tags=["token"])

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    
    # DB에서 사용자를 찾기
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    # 비밀번호 검증 (입력값 vs 저장된 해시된 비밀번호)
    if not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    # JWT 토큰 생성 (id 추가)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
    data={"sub": str(user.id), "email": user.email, "role": user.role},  # id를 문자열로 변환
    expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
