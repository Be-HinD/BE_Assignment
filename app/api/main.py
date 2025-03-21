# app/api/main.py (일부)
from fastapi import APIRouter
from app.api.routes.admin import admin_reservation
from app.api.routes.user import users, token, reservation  # token 모듈 추가

api_router = APIRouter()
api_router.include_router(users.router)            # /v1/users/...
api_router.include_router(admin_reservation.router)
api_router.include_router(token.router)            # /v1/token
api_router.include_router(reservation.router)