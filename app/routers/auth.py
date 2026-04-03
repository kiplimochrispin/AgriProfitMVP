from fastapi import APIRouter, HTTPException, status

from app.schemas import LoginRequest, TokenResponse
from app.security import authenticate_admin, create_access_token

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    if not authenticate_admin(payload.username, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return TokenResponse(access_token=create_access_token(payload.username))
