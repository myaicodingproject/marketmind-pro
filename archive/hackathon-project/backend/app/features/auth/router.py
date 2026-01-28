from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.auth.schemas import UserCreate, UserLogin, Token, UserResponse
from app.features.auth.service import AuthService

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await AuthService.create_user(db, user_data)
    access_token = AuthService.create_access_token({"sub": user.email})
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await AuthService.authenticate_user(db, credentials.email, credentials.password)
    access_token = AuthService.create_access_token({"sub": user.email})
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )