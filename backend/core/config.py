from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    API_HOST: str = "localhost"
    API_PORT: int = 8000

    DEBUG: bool = False

    DATABASE_URL: str


    ALLOWED_ORIGINS: str = ""
    ALLOWED_METHODS: str = "*"
    ALLOWED_HEADERS: str = "*"

    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> List[str]:
        return v.split(",") if v else []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
