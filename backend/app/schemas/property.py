from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PropertyBase(BaseModel):
    title: str
    description: str
    price: float
    property_type: str
    location: str
    bedrooms: int
    bathrooms: int
    area: int
    images: List[str] = Field(default_factory=list)
    status: str = "active"

class PropertyCreate(PropertyBase):
    pass

class PropertyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    property_type: Optional[str] = None
    location: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[int] = None
    images: Optional[List[str]] = None
    status: Optional[str] = None

class Property(PropertyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 