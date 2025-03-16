from fastapi import APIRouter, Depends, HTTPException


router = APIRouter(prefix="/users", tags=["users"])

@router.get(
    "/",
    # dependencies=[Depends(get_current_active_superuser)],
    # response_model=UsersPublic,
)
def read_users():
    
    return "Hello"