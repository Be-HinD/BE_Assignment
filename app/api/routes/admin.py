from fastapi import APIRouter, Depends
from app.core.security import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/test")
async def admin_dashboard(current_admin: dict = Depends(get_current_admin_user)):
    return {"message": f"Welcome, {current_admin['username']}! This is the admin dashboard."}
