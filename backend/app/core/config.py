"""
Core configuration settings.
"""

from pydantic_settings import BaseSettings  # 🔧 FIXED: Changed import
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App settings
    app_name: str = "Arabic Legal Assistant"
    debug: bool = False
    version: str = "2.0.0"
    
    # Database
    database_url: str = "sqlite:///./arabic_legal.db"
    
    # Authentication
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI (🔧 FIXED: Changed from openai_api_key to match your .env)
    deepseek_api_key: str
    
    # ChromaDB
    chroma_persist_dir: str = "./chroma_db"
    
    # CORS
    allowed_origins: List[str] = [
    "https://moaen.ai",
    "https://www.moaen.ai",
    "http://localhost:3000",  # Keep for development
    "http://127.0.0.1:3000"   # Keep for development
]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()