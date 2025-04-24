from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..models.property import Property, PropertyCreate, PropertyUpdate
from ..services.property_service import PropertyService

router = APIRouter()
property_service = PropertyService()

@router.post("/", response_model=Property)
async def create_property(property_data: PropertyCreate):
    return await property_service.create_property(property_data)

@router.get("/{property_id}", response_model=Property)
async def get_property(property_id: str):
    property = await property_service.get_property(property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property

@router.get("/", response_model=List[Property])
async def list_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    location: Optional[str] = None
):
    return await property_service.list_properties(
        skip=skip,
        limit=limit,
        property_type=property_type,
        min_price=min_price,
        max_price=max_price,
        location=location
    )

@router.put("/{property_id}", response_model=Property)
async def update_property(property_id: str, property_data: PropertyUpdate):
    property = await property_service.update_property(property_id, property_data)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property

@router.delete("/{property_id}")
async def delete_property(property_id: str):
    success = await property_service.delete_property(property_id)
    if not success:
        raise HTTPException(status_code=404, detail="Property not found")
    return {"message": "Property deleted successfully"} 