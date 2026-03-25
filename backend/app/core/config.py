from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import json

class Settings(BaseSettings):
    PROJECT_NAME: str = "OCR Scan-to-PDF Engine"
    API_V1_STR: str = "/api/v1"
    
    # OCR Settings
    OCR_LANGUAGES: List[str] = ["en"]
    
    # CORS (can be a JSON list or comma separated)
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Storage (local for now)
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
