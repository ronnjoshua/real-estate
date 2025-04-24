from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    ADMIN = "admin"
    CLIENT = "client"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.CLIENT

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class User(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[UserRole] = None

class InvitationCreate(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.CLIENT
    expires_at: Optional[datetime] = None

class Invitation(InvitationCreate):
    id: str
    token: str
    created_at: datetime
    is_used: bool = False

    class Config:
        from_attributes = True 