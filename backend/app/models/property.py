from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PropertyBase(BaseModel):
    title: str
    description: str
    price: float
    location: str
    property_type: str
    bedrooms: int
    bathrooms: int
    area: float
    images: List[str] = []
    features: List[str] = []
    status: str = "available"  # available, sold, rented
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PropertyCreate(PropertyBase):
    pass

class PropertyUpdate(PropertyBase):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    images: Optional[List[str]] = None
    features: Optional[List[str]] = None
    status: Optional[str] = None

class Property(PropertyBase):
    id: str 