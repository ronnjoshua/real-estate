from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
import os
import logging
from pathlib import Path
import re

logger = logging.getLogger(__name__)

def read_env_file(file_path=None):
    """
    Read environment variables directly from .env file.
    This is a simpler approach than using python-dotenv, 
    and may work better with complex values like private keys.
    """
    if file_path is None:
        backend_dir = Path(__file__).parent.parent.parent
        file_path = backend_dir / '.env'
    
    if not Path(file_path).exists():
        logger.warning(f"Cannot find .env file at {file_path}")
        return
        
    logger.info(f"Reading environment variables from {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                try:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value
                        logger.debug(f"Set environment variable: {key}")
                except Exception as e:
                    logger.warning(f"Error parsing line in .env file: {line}")
    except Exception as e:
        logger.error(f"Error reading .env file: {e}")

# Read environment variables from .env file
read_env_file()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Real Estate API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security Configuration
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        env="ALLOWED_ORIGINS"
    )
    
    def get_allowed_origins(self) -> list[str]:
        """Parse ALLOWED_ORIGINS environment variable into a list."""
        import json
        try:
            # Try to parse as JSON array first (Railway format)
            if self.ALLOWED_ORIGINS.startswith('['):
                return json.loads(self.ALLOWED_ORIGINS)
            # Otherwise treat as comma-separated string
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        except (json.JSONDecodeError, AttributeError):
            # Fallback to splitting by comma
            return [origin.strip() for origin in str(self.ALLOWED_ORIGINS).split(",") if origin.strip()]
    
    # Database Configuration
    DATABASE_URL: str = Field(default="", env="DATABASE_URL")
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from .env file

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 