# app/api/routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from sqlalchemy import text

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
def read_users(db: Session = Depends(get_db)):

    # 예시 : 직접 SQL문 실행
    result = db.execute(text("SELECT * FROM users")).fetchall()
    return {"users": [dict(row) for row in result]}
