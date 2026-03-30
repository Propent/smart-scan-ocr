from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Union
from pydantic import field_validator
import json

class Settings(BaseSettings):
    PROJECT_NAME: str = "OCR Scan-to-PDF Engine"
    API_V1_STR: str = "/api/v1"
    
    # OCR Settings
    OCR_LANGUAGES: List[str] = ["en"]
    
    # CORS (can be a JSON list or comma separated)
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v

    # Storage (local for now)
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
