import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application Configuration Settings"""
    
    redis_url: str = "redis://redis:6379/"

    # AI Configs
    groq_api_key: str = ""
    whisper_model_size: str = "small"
    deepface_backend: str = "mediapipe"
    
    # Business logic
    interview_duration_seconds: int = 600

    class Config:
        env_file = os.getenv("ENV_FILE_PATH", ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
