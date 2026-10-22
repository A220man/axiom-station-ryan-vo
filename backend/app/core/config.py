from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Axiom Station"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    DATABASE_URL: str = "sqlite:///./axiom_station.db"
    SECRET_KEY: str = "dev-secret-change-in-production"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()