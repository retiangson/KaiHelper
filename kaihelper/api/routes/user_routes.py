"""
User endpoints: register, login, profile
"""
from fastapi import APIRouter, HTTPException, Request
from kaihelper.contracts.user_dto import RegisterUserDTO, LoginRequestDTO

router = APIRouter()

@router.post("/register")
def register_user(dto: RegisterUserDTO, request: Request):
    user_service = request.app.state.services.get_user_service()
    result = user_service.register_user(dto)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}

@router.post("/login")
def login_user(dto: LoginRequestDTO, request: Request):
    user_service = request.app.state.services.get_user_service()
    result = user_service.login_user(dto)
    if not result.success:
        raise HTTPException(status_code=401, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}

@router.get("/profile/{user_id}")
def get_profile(user_id: int, request: Request):
    user_service = request.app.state.services.get_user_service()
    result = user_service.get_user_profile(user_id)
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}
