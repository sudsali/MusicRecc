# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = "key"
    SPARK_MASTER: str = "local[*]"
    APP_NAME: str = "MusicRecommendation"

    class Config:
        env_file = ".env"

settings = Settings()
