from pydantic_settings import BaseSettings
from pydantic import Field
import os
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    MODEL_NAME: str = "gemini-2.0-flash"
    OUTPUT_FOLDER: str = "output_1"
    MAX_CONCURRENCY: int = 10
    MAX_OUTPUT_TOKENS: int = 8192
    API_BASE_URL: str 
    FASTAPI_KEY: str = "your-api-key-here"  # Change this in production
    
    # API base URL for callbacks
    API_BASE_URL: Optional[str] = Field(
        os.environ.get("API_BASE_URL", "https://api-dev.maverickcosts.com"),
        description="Base URL for API callbacks"
    )
    
    # Background task settings
    MAX_TASK_RUNTIME: int = Field(
        os.environ.get("MAX_TASK_RUNTIME", 3600),  # 1 hour default
        description="Maximum runtime for background tasks in seconds"
    )
    
    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    
    
    # API settings
    API_CONCURRENCY_LIMIT: int = int(os.getenv("API_CONCURRENCY_LIMIT", 10))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()
