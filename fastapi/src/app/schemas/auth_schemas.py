from pydantic import BaseModel, EmailStr, constr


class TokenRefresh(BaseModel):
    refresh_token: str


class Token(TokenRefresh):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserSchema(BaseModel):
    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None


class CreateUserSchema(UserSchema):
    password: constr(min_length=8)
    password_confirm: str


class UserInDB(UserSchema):
    password: str
