from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "AI Research Workspace"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
