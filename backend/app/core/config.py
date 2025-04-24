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

# Check if key Firebase variables are set
firebase_vars = [
    "FIREBASE_TYPE",
    "FIREBASE_PROJECT_ID",
    "FIREBASE_PRIVATE_KEY_ID",
    "FIREBASE_PRIVATE_KEY",
    "FIREBASE_CLIENT_EMAIL",
    "FIREBASE_CLIENT_ID"
]

missing_vars = [var for var in firebase_vars if not os.environ.get(var)]
if missing_vars:
    logger.warning(f"Missing Firebase environment variables: {', '.join(missing_vars)}")
else:
    logger.info("All required Firebase environment variables are set")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Real Estate API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Firebase credentials as a dictionary
    FIREBASE_CREDENTIALS: dict = Field(
        default_factory=lambda: {
            "type": os.environ.get("FIREBASE_TYPE", "service_account"),
            "project_id": os.environ.get("FIREBASE_PROJECT_ID", ""),
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID", ""),
            "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
            "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL", ""),
            "client_id": os.environ.get("FIREBASE_CLIENT_ID", ""),
            "auth_uri": os.environ.get("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": os.environ.get("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": os.environ.get("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL", ""),
        }
    )
    
    # Debugging: Log credentials presence but not their values
    def log_credentials_status(self):
        """Log which Firebase credentials are present without revealing sensitive values"""
        creds_dict = self.FIREBASE_CREDENTIALS
        logger.info("Checking Firebase credentials:")
        for key in creds_dict:
            if key == 'private_key':
                has_value = bool(creds_dict.get(key, "").strip())
                logger.info(f"  - {key}: {'Present' if has_value else 'Missing or empty'}")
            else:
                has_value = bool(creds_dict.get(key, "").strip())
                value_preview = creds_dict.get(key, "")[:5] + "..." if has_value else "N/A"
                logger.info(f"  - {key}: {value_preview if has_value else 'Missing or empty'}")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from .env file

@lru_cache()
def get_settings():
    settings = Settings()
    # Log credentials status at startup
    settings.log_credentials_status()
    return settings

settings = get_settings() 