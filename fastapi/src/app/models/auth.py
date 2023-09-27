from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(default=None, nullable=False, primary_key=True)
    email: str
    username: str
    full_name: str
    password: str
    is_active: bool = Field(default=True, nullable=False)
