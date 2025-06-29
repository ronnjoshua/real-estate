from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from app.models.user import (
    User, UserCreate, UserRole, Token,
    InvitationCreate, Invitation
)
from app.core.security import (
    verify_password,
    get_password_hash,
    generate_invitation_token,
    validate_password_strength,
    validate_email,
    check_rate_limit
)
from app.core.auth import (
    create_token_pair,
    verify_token
)
from app.core.config import get_settings
from app.db.memory_db import (
    get_user_by_email,
    create_user,
    create_invitation,
    get_invitation_by_token,
    mark_invitation_as_used,
    update_user
)
from app.api.v1.deps import get_current_admin, get_current_active_user
from pydantic import BaseModel, Field

settings = get_settings()

class UpdateProfileRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    current_password: Optional[str] = None
    new_password: Optional[str] = Field(None, min_length=8)

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

router = APIRouter()

@router.post("/token", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return access and refresh tokens"""
    
    # Rate limiting check
    if not check_rate_limit(form_data.username):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Validate email format
    if not validate_email(form_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    user = get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token pair
    token_data = {
        "sub": user.email,
        "role": user.role.value,
        "user_id": str(user.id)
    }
    
    tokens = create_token_pair(token_data)
    
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": tokens["token_type"],
        "expires_in": tokens["expires_in"],
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value
        }
    }

@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    payload = verify_token(refresh_data.refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_email(user_email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new token pair
    token_data = {
        "sub": user.email,
        "role": user.role.value,
        "user_id": str(user.id)
    }
    
    tokens = create_token_pair(token_data)
    
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": tokens["token_type"],
        "expires_in": tokens["expires_in"]
    }


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.post("/invite", response_model=Invitation)
async def invite_user(invitation: InvitationCreate, _: User = Depends(get_current_admin)):
    token = generate_invitation_token()
    # Set expiration to 7 days from now if not provided
    expires_at = invitation.expires_at or datetime.utcnow() + timedelta(days=7)
    db_invitation = create_invitation(
        email=invitation.email,
        role=invitation.role,
        token=token,
        expires_at=expires_at
    )
    return db_invitation

@router.get("/invitations", response_model=list)
async def get_invitations(_: User = Depends(get_current_admin)):
    """Get all invitations (admin only)"""
    from app.db.memory_db import get_all_invitations
    return get_all_invitations()

@router.post("/accept-invitation/{token}", response_model=User)
async def accept_invitation(token: str, user: UserCreate):
    invitation = get_invitation_by_token(token)
    if not invitation or invitation.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or used invitation token"
        )
    if invitation.expires_at and invitation.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )
    
    db_user = get_user_by_email(user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = create_user(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=invitation.role
    )
    
    mark_invitation_as_used(token)
    return db_user

@router.put("/update-profile", response_model=User)
async def update_profile(
    update_data: UpdateProfileRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Update user profile with validation"""
    
    # Validate email format if changed
    if update_data.email != current_user.email:
        if not validate_email(update_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        existing_user = get_user_by_email(update_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # If changing password, verify current password and validate new password
    if update_data.new_password:
        if not update_data.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required to set new password"
            )
        
        if not validate_password_strength(update_data.new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long and contain uppercase, lowercase, digit, and special character"
            )
        
        db_user = get_user_by_email(current_user.email)
        if not verify_password(update_data.current_password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )

    # Update user
    updated_user = update_user(
        email=current_user.email,
        updates={
            "full_name": update_data.full_name,
            "email": update_data.email,
            "hashed_password": get_password_hash(update_data.new_password) if update_data.new_password else None
        }
    )

    return updated_user

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout user (client-side token removal required)"""
    # In a production system with Redis, you would blacklist the token here
    return {"message": "Successfully logged out"}

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user)
):
    """Change user password"""
    
    # Validate new password strength
    if not validate_password_strength(new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long and contain uppercase, lowercase, digit, and special character"
        )
    
    # Verify current password
    db_user = get_user_by_email(current_user.email)
    if not verify_password(current_password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    update_user(
        email=current_user.email,
        updates={"hashed_password": get_password_hash(new_password)}
    )
    
    return {"message": "Password changed successfully"} 