import os
from pydantic_settings import BaseSettings, SettingsConfigDict  
from functools import lru_cache

class Settings(BaseSettings):

    DB_USERNAME=str
    DB_PASSWORD=str
    DB_HOSTNAME=str
    DB_PORT=int
    DB_NAME=str

    DATABASE_URL=str

    SECRET_KEY=str
    ALGORITHM=str
    ACCESS_TOKEN_EXPIRE_MINUTES=int

    REDIS_URL=str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

@lru_cache
def get_settings() :
    return Settings()