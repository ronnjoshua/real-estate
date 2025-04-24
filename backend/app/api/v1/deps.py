from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import get_current_user
from app.db.memory_db import get_user_by_email
from app.models.user import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token, get_user_by_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Temporarily return a mock user for development
    return {
        "id": "1",
        "email": "test@example.com",
        "is_active": True
    } 