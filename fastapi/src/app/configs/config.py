from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_PORT: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_HOST: str = ""
    POSTGRES_HOSTNAME: str = ""
    DATABASE_URL: str = ""
    ACCESS_TOKEN_EXPIRES_IN: int = 30
    REFRESH_TOKEN_EXPIRES_IN: int = 60
    JWT_ALGORITHM: str = ""
    CLIENT_ORIGIN: str = ""
    JWT_PRIVATE_KEY: str = ""
    JWT_PUBLIC_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
