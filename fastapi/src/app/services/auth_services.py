from datetime import datetime, timedelta
from typing import Annotated

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.configs.config import settings
from src.app.configs.database import get_session
from src.app.models.auth import User
from src.app.schemas.auth_schemas import TokenData, UserInDB, UserSchema

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

ALGORITHM = settings.JWT_ALGORITHM
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
SECRET_KEY = settings.JWT_PUBLIC_KEY
REFRESH_KEY = settings.JWT_PRIVATE_KEY
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username: str, db: AsyncSession):
    query = select(User).where(User.username == username)
    user = await db.exec(query)
    data = user.first()
    if data:
        user_dict = data.dict()
        return UserInDB(**user_dict)


async def authenticate_user(username: str, password: str, db: AsyncSession):
    user = await get_user(username, db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None, refresh_token: bool = False):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    if refresh_token:
        key = REFRESH_KEY
    else:
        key = SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, key, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        time_exp: float = payload.get("exp")
        if datetime.fromtimestamp(time_exp) < datetime.now():
            raise credentials_exception
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    async_session = get_session()
    session = await async_session.__anext__()
    user = await get_user(username=token_data.username, db=session)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[UserSchema, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def action_refresh_token(refresh_token: str, access_token_expires: timedelta | None = None):
    try:
        # Decode the refresh token to get the user data
        payload = jwt.decode(refresh_token, REFRESH_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid refresh token")

    # Generate and return a new access token
    access_token = create_access_token(data={"sub": payload.get("sub")}, expires_delta=access_token_expires)

    return access_token
