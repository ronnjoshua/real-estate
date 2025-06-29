from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PropertyType(str, Enum):
    HOUSE = "house"
    APARTMENT = "apartment"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    COMMERCIAL = "commercial"
    LAND = "land"

class PropertyStatus(str, Enum):
    AVAILABLE = "available"
    SOLD = "sold"
    RENTED = "rented"
    PENDING = "pending"
    INACTIVE = "inactive"

class PropertyLocation(BaseModel):
    address: str
    city: str
    state: str
    zip_code: str
    country: str = "US"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    neighborhood: Optional[str] = None

class PropertyFeatures(BaseModel):
    parking_spaces: Optional[int] = 0
    has_garage: bool = False
    has_pool: bool = False
    has_garden: bool = False
    has_balcony: bool = False
    has_basement: bool = False
    has_attic: bool = False
    is_furnished: bool = False
    pet_friendly: bool = False
    year_built: Optional[int] = None
    lot_size: Optional[float] = None  # in square feet
    hoa_fee: Optional[float] = None
    property_tax: Optional[float] = None

class PropertyMedia(BaseModel):
    images: List[str] = []
    virtual_tour_url: Optional[str] = None
    video_url: Optional[str] = None
    floor_plan_url: Optional[str] = None
    documents: List[str] = []  # URLs to property documents

class PropertyBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    price: float = Field(..., gt=0)
    location: PropertyLocation
    property_type: PropertyType
    bedrooms: int = Field(..., ge=0, le=20)
    bathrooms: float = Field(..., ge=0, le=20)
    area: float = Field(..., gt=0)  # in square feet
    features: PropertyFeatures = Field(default_factory=PropertyFeatures)
    media: PropertyMedia = Field(default_factory=PropertyMedia)
    status: PropertyStatus = PropertyStatus.AVAILABLE
    agent_id: Optional[str] = None
    tags: List[str] = []
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('area')
    def area_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Area must be positive')
        return v

class PropertyCreate(PropertyBase):
    pass

class PropertyUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    price: Optional[float] = Field(None, gt=0)
    location: Optional[PropertyLocation] = None
    property_type: Optional[PropertyType] = None
    bedrooms: Optional[int] = Field(None, ge=0, le=20)
    bathrooms: Optional[float] = Field(None, ge=0, le=20)
    area: Optional[float] = Field(None, gt=0)
    features: Optional[PropertyFeatures] = None
    media: Optional[PropertyMedia] = None
    status: Optional[PropertyStatus] = None
    agent_id: Optional[str] = None
    tags: Optional[List[str]] = None

class Property(PropertyBase):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
class PropertyFilters(BaseModel):
    """Filters for property search and listing"""
    property_type: Optional[PropertyType] = None
    status: Optional[PropertyStatus] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    min_bedrooms: Optional[int] = Field(None, ge=0)
    max_bedrooms: Optional[int] = Field(None, ge=0)
    min_bathrooms: Optional[float] = Field(None, ge=0)
    max_bathrooms: Optional[float] = Field(None, ge=0)
    min_area: Optional[float] = Field(None, ge=0)
    max_area: Optional[float] = Field(None, ge=0)
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    has_garage: Optional[bool] = None
    has_pool: Optional[bool] = None
    has_garden: Optional[bool] = None
    pet_friendly: Optional[bool] = None
    year_built_min: Optional[int] = None
    year_built_max: Optional[int] = None
    
class PropertySearchParams(BaseModel):
    """Search parameters for property queries"""
    q: Optional[str] = Field(None, description="Search query")
    filters: Optional[PropertyFilters] = None
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")
    skip: int = Field(0, ge=0, description="Number of properties to skip")
    limit: int = Field(10, ge=1, le=100, description="Number of properties to return")

class PropertyResponse(BaseModel):
    """Response model for property listing"""
    properties: List[Property]
    total: int
    skip: int
    limit: int
    has_more: bool 