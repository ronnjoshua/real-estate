from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import secrets
import string
import re
from app.models.user import User, UserRole
from app.core.config import get_settings
from fastapi import HTTPException, status

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def generate_invitation_token(length: int = 32) -> str:
    """Generate secure invitation token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def get_current_user_from_token(email: str) -> Optional[User]:
    """Get user by email for token validation"""
    try:
        # Import here to avoid circular dependency
        from app.db.memory_db import get_user_by_email
        return get_user_by_email(email)
    except Exception:
        return None

def validate_password_strength(password: str) -> bool:
    """Validate password meets security requirements"""
    if len(password) < 8:
        return False
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

def validate_email(email: str) -> bool:
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def generate_secure_filename(filename: str) -> str:
    """Generate secure filename for file uploads"""
    # Remove any path separators and keep only filename
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Generate a unique prefix
    prefix = secrets.token_hex(8)
    
    # Sanitize filename - keep only alphanumeric, dots, hyphens, underscores
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    
    return f"{prefix}_{safe_filename}"

def check_rate_limit(identifier: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
    """Simple rate limiting check (in production, use Redis)"""
    # This is a simplified implementation
    # In production, implement proper rate limiting with Redis
    return True 