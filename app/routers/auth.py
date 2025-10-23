"""
Authentication endpoints.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.interviewers import User, UserCreate, Token
from app.services.interviewers_service import AuthService
from app.utils.security import create_access_token, verify_token, verify_api_key
from app.config import settings
from app.logging_config import logger

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_api_key)])
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    logger.info("auth.register.requested", extra={"email": user.email, "username": user.username})

    if AuthService.get_user_by_email(db, user.email):
        logger.info("auth.register.duplicate_email", extra={"email": user.email})

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if AuthService.get_user_by_username(db, user.username):
        logger.info("auth.register.duplicate_username", extra={"username": user.username})

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    return AuthService.create_user(db, user)

@router.post("/login", response_model=Token, dependencies=[Depends(verify_api_key)])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    logger.info("auth.login.requested", extra={"username": form_data.username})

    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.info("auth.login.failed", extra={"username": form_data.username, "reason": "bad_credentials"})

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.info("auth.login.succeeded", extra={"user_id": user.id, "username": user.username, "expires_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "id": user.id,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    logger.info("auth.refresh.requested")

    # Implement refresh token logic
    username = verify_token(refresh_token)
    if not username:
        logger.info("auth.refresh.failed", extra={"reason": "invalid_token"})

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = AuthService.get_user_by_username(db, username)
    if not user or not user.is_active:
        logger.info("auth.refresh.failed", extra={"reason": "user_inactive_or_missing", "username": username})

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    logger.info("auth.refresh.succeeded", extra={"user_id": user.id, "username": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }