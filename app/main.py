# app/main.py
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.database.base import Base
from app.database.session import engine

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

app = FastAPI(
    title="Assignment",
    generate_unique_id_function=custom_generate_unique_id,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/v1")

# 애플리케이션 시작 시 모델을 임포트한 후 테이블 생성
@app.on_event("startup")
def on_startup():
    # 모델 임포트
    import app.models.user

    Base.metadata.create_all(bind=engine)
