from datetime import timedelta
from typing import Annotated

from pydantic import EmailStr
from sqlmodel import or_, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.configs.config import settings
from src.app.configs.database import get_session
from src.app.models.auth import User
from src.app.schemas.auth_schemas import CreateUserSchema, Token, UserSchema
from src.app.services.auth_services import (
    action_refresh_token,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
)

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN


router = APIRouter(prefix="/api/auth")


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_session)
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    refresh_token = create_access_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires, refresh_token=True
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(refresh_token: str):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN)
    access_token = await action_refresh_token(refresh_token, access_token_expires)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=UserSchema)
async def read_users_me(current_user: Annotated[UserSchema, Depends(get_current_active_user)]):
    return current_user


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
async def create_user(payload: CreateUserSchema, db: AsyncSession = Depends(get_session)):
    # Check if user already exist
    user_email_statement = select(User).where(
        or_(User.email == EmailStr(payload.email.lower()), User.username == payload.username.lower())
    )
    user = await db.exec(user_email_statement)
    if user.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or username already exist")
    # Compare password and passwordConfirm
    if payload.password != payload.password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    #  Hash the password
    payload.password = get_password_hash(payload.password)
    del payload.password_confirm
    payload.email = EmailStr(payload.email.lower())
    new_user = User(**payload.dict())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
