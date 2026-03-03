from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from app.services.auth_service import AuthService

router = APIRouter(tags=["auth"])

class LoginRequest(BaseModel):
    identifier: str # Supports both email and username
    password: str

def get_auth_service():
    return AuthService()

@router.post("/login")
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.authenticate_user(request.identifier, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid identifier or password"
        )

    return {"message": "Login successful", "user": user}
