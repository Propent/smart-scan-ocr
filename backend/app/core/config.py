from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Union, Any
from pydantic import field_validator, Field
import json

class Settings(BaseSettings):
    PROJECT_NAME: str = "OCR Scan-to-PDF Engine"
    API_V1_STR: str = "/api/v1"
    
    # OCR Settings
    OCR_LANGUAGES: List[str] = ["en"]
    
    # CORS - Use str to avoid Pydantic's automatic list parsing which fails on Render
    BACKEND_CORS_ORIGINS_RAW: str = Field("*", alias="BACKEND_CORS_ORIGINS")

    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        v = self.BACKEND_CORS_ORIGINS_RAW
        if not v or v == "*":
            return ["*"]
        
        if isinstance(v, str):
            # If it looks like a JSON list
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    # Fallback: remove brackets and quotes, then split by comma
                    clean_v = v.strip("[]").replace("'", "").replace('"', "")
                    return [i.strip() for i in clean_v.split(",") if i.strip()]
            # If it's just a comma-separated string
            return [i.strip() for i in v.split(",") if i.strip()]
        return ["*"]

    # Storage (local for now)
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"

    class Config:
        case_sensitive = True
        env_file = ".env"
        # Allow extra fields so the raw alias doesn't conflict
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings()
