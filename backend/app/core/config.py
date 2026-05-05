from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "AI Research Workspace"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_db_path: str = "./chroma_db"

    groq_api_key: str = ""
    groq_model: str = "llama3-8b-8192"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
