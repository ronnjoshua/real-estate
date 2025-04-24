from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional
from app.models.user import (
    User, UserCreate, UserRole, Token, TokenData,
    InvitationCreate, Invitation
)
from app.core.security import (
    verify_password,
    get_password_hash,
    get_current_user,
    generate_invitation_token
)
from app.core.auth import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.db.memory_db import (
    get_user_by_email,
    create_user,
    create_invitation,
    get_invitation_by_token,
    mark_invitation_as_used,
    update_user
)
from app.api.v1.deps import get_current_admin
from pydantic import BaseModel

class UpdateProfileRequest(BaseModel):
    full_name: str
    email: str
    current_password: Optional[str] = None
    new_password: Optional[str] = None

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=User)
async def register(user: UserCreate):
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
        role=user.role
    )
    return db_user

@router.get("/me", response_model=User)
async def read_users_me(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token, get_user_by_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/invite", response_model=Invitation)
async def invite_user(invitation: InvitationCreate, _: User = Depends(get_current_admin)):
    token = generate_invitation_token()
    db_invitation = create_invitation(
        email=invitation.email,
        role=invitation.role,
        token=token,
        expires_at=invitation.expires_at
    )
    return db_invitation

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
    token: str = Depends(oauth2_scheme)
):
    current_user = get_current_user(token, get_user_by_email)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    # Check if email is being changed and if it's already taken
    if update_data.email != current_user.email:
        existing_user = get_user_by_email(update_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # If changing password, verify current password
    if update_data.new_password:
        if not update_data.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required to set new password"
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