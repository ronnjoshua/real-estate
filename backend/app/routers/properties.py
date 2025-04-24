from fastapi import APIRouter, HTTPException, Depends, Query, status, Request
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from ..services.firestore import FirestoreService
import logging
import json
import time

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()

class PropertyBase(BaseModel):
    title: str
    description: str
    price: float
    location: str
    bedrooms: int
    bathrooms: float
    area: float
    images: List[str]
    property_type: str
    status: str

class PropertyCreate(PropertyBase):
    pass

class PropertyUpdate(PropertyBase):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    area: Optional[float] = None
    images: Optional[List[str]] = None
    property_type: Optional[str] = None
    status: Optional[str] = None

class Property(PropertyBase):
    id: str

class ResponseMessage(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None

def get_firestore_service():
    return FirestoreService()

@router.get("/properties", response_model=List[Property])
async def get_properties(request: Request, firestore: FirestoreService = Depends(get_firestore_service)):
    log_request_info(request)
    start_time = time.time()
    
    try:
        logger.info("Fetching all properties")
        properties = await firestore.get_all_properties()
        
        elapsed = time.time() - start_time
        logger.info(f"Successfully retrieved {len(properties)} properties in {elapsed:.2f}s")
        
        # Convert any Firestore timestamp objects to strings
        for prop in properties:
            if 'created_at' in prop and hasattr(prop['created_at'], 'isoformat'):
                prop['created_at'] = prop['created_at'].isoformat()
            if 'updated_at' in prop and hasattr(prop['updated_at'], 'isoformat'):
                prop['updated_at'] = prop['updated_at'].isoformat()
        
        return properties
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Error fetching properties after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch properties: {str(e)}"
        )

@router.get("/properties/search", response_model=List[Property])
async def search_properties(
    request: Request,
    q: str = Query(..., description="Search query"),
    firestore: FirestoreService = Depends(get_firestore_service)
):
    log_request_info(request)
    start_time = time.time()
    
    try:
        logger.info(f"Searching properties with query: '{q}'")
        properties = await firestore.search_properties(q)
        
        elapsed = time.time() - start_time
        logger.info(f"Found {len(properties)} properties matching query: '{q}' in {elapsed:.2f}s")
        
        # Convert any Firestore timestamp objects to strings
        for prop in properties:
            if 'created_at' in prop and hasattr(prop['created_at'], 'isoformat'):
                prop['created_at'] = prop['created_at'].isoformat()
            if 'updated_at' in prop and hasattr(prop['updated_at'], 'isoformat'):
                prop['updated_at'] = prop['updated_at'].isoformat()
        
        return properties
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Error searching properties with query '{q}' after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to search properties: {str(e)}"
        )

@router.get("/properties/{property_id}", response_model=Property)
async def get_property(
    property_id: str,
    request: Request,
    firestore: FirestoreService = Depends(get_firestore_service)
):
    log_request_info(request)
    start_time = time.time()
    
    try:
        logger.info(f"Fetching property with ID: {property_id}")
        
        # Try to fetch the property
        property_data = await firestore.get_property_by_id(property_id)
        
        # If not found, try with different ID formats (some systems use numeric IDs)
        if not property_data and property_id.isdigit():
            # Try with just the numeric ID
            logger.info(f"Trying to fetch property with numeric ID: {property_id}")
            property_data = await firestore.get_property_by_id(property_id)
        
        elapsed = time.time() - start_time
        if not property_data:
            logger.warning(f"Property not found with ID: {property_id} after {elapsed:.2f}s")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Property with ID {property_id} not found"
            )
        
        # Convert any Firestore timestamp objects to strings
        if 'created_at' in property_data and hasattr(property_data['created_at'], 'isoformat'):
            property_data['created_at'] = property_data['created_at'].isoformat()
        if 'updated_at' in property_data and hasattr(property_data['updated_at'], 'isoformat'):
            property_data['updated_at'] = property_data['updated_at'].isoformat()
        
        logger.info(f"Successfully retrieved property: {property_id} in {elapsed:.2f}s")
        return property_data
    except HTTPException:
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Error fetching property {property_id} after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch property: {str(e)}"
        )

@router.post("/properties", response_model=Property, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: PropertyCreate,
    request: Request,
    firestore: FirestoreService = Depends(get_firestore_service)
):
    log_request_info(request)
    start_time = time.time()
    
    try:
        logger.info(f"Creating new property: {property_data.title}")
        
        # Convert to dict for Firestore
        property_dict = property_data.dict()
        
        new_property = await firestore.create_property(property_dict)
        
        elapsed = time.time() - start_time
        logger.info(f"Successfully created property with ID: {new_property['id']} in {elapsed:.2f}s")
        
        # Convert any Firestore timestamp objects to strings
        if 'created_at' in new_property and hasattr(new_property['created_at'], 'isoformat'):
            new_property['created_at'] = new_property['created_at'].isoformat()
        if 'updated_at' in new_property and hasattr(new_property['updated_at'], 'isoformat'):
            new_property['updated_at'] = new_property['updated_at'].isoformat()
        
        return new_property
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Error creating property after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to create property: {str(e)}"
        )

@router.put("/properties/{property_id}", response_model=Property)
async def update_property(
    property_id: str,
    property_update: PropertyUpdate,
    request: Request,
    firestore: FirestoreService = Depends(get_firestore_service)
):
    log_request_info(request)
    start_time = time.time()
    
    try:
        update_data = {k: v for k, v in property_update.dict().items() if v is not None}
        logger.info(f"Updating property with ID: {property_id}")
        
        updated_property = await firestore.update_property(property_id, update_data)
        
        elapsed = time.time() - start_time
        if not updated_property:
            logger.warning(f"Property not found for update with ID: {property_id} after {elapsed:.2f}s")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Property with ID {property_id} not found"
            )
        
        # Convert any Firestore timestamp objects to strings
        if 'created_at' in updated_property and hasattr(updated_property['created_at'], 'isoformat'):
            updated_property['created_at'] = updated_property['created_at'].isoformat()
        if 'updated_at' in updated_property and hasattr(updated_property['updated_at'], 'isoformat'):
            updated_property['updated_at'] = updated_property['updated_at'].isoformat()
        
        logger.info(f"Successfully updated property: {property_id} in {elapsed:.2f}s")
        return updated_property
    except HTTPException:
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Error updating property {property_id} after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to update property: {str(e)}"
        )

@router.delete("/properties/{property_id}", response_model=ResponseMessage)
async def delete_property(
    property_id: str,
    request: Request,
    firestore: FirestoreService = Depends(get_firestore_service)
):
    log_request_info(request)
    start_time = time.time()
    
    try:
        logger.info(f"Deleting property with ID: {property_id}")
        success = await firestore.delete_property(property_id)
        
        elapsed = time.time() - start_time
        if not success:
            logger.warning(f"Property not found for deletion with ID: {property_id} after {elapsed:.2f}s")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Property with ID {property_id} not found"
            )
        
        logger.info(f"Successfully deleted property: {property_id} in {elapsed:.2f}s")
        return ResponseMessage(message="Property deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Error deleting property {property_id} after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to delete property: {str(e)}"
        )

def log_request_info(request: Request):
    """Log information about the incoming request."""
    client = request.client.host if request.client else "unknown"
    method = request.method
    url = str(request.url)
    logger.info(f"Request from {client}: {method} {url}") 