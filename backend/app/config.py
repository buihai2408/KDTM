"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql://finance_user:finance_pass@localhost:5432/finance_db"
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Service Keys
    DIFY_SERVICE_KEY: str = "dify-service-key"
    N8N_SERVICE_KEY: str = "n8n-service-key"
    N8N_WEBHOOK_URL: str = "http://n8n:5678"
    
    # Application
    APP_NAME: str = "Personal Finance BI System"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
