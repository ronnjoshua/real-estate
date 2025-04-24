from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.db.memory_db import (
    get_properties,
    get_property,
    create_property,
    update_property,
    delete_property
)

router = APIRouter()

@router.get("/", response_model=List[dict])
async def list_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    location: Optional[str] = None
):
    return get_properties(
        skip=skip,
        limit=limit,
        property_type=property_type,
        min_price=min_price,
        max_price=max_price,
        location=location
    )

@router.get("/{property_id}", response_model=dict)
async def read_property(property_id: str):
    property = get_property(property_id)
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    return property

@router.post("/", response_model=dict)
async def create_property_endpoint(property: dict):
    return create_property(property)

@router.put("/{property_id}", response_model=dict)
async def update_property_endpoint(property_id: str, property: dict):
    updated_property = update_property(property_id, property)
    if not updated_property:
        raise HTTPException(status_code=404, detail="Property not found")
    return updated_property

@router.delete("/{property_id}")
async def delete_property_endpoint(property_id: str):
    if not delete_property(property_id):
        raise HTTPException(status_code=404, detail="Property not found")
    return {"message": "Property deleted successfully"} 