from fastapi import APIRouter, HTTPException, Depends, Query, status, Request
from typing import List, Optional, Dict, Any
from app.models.property import (
    Property, PropertyCreate, PropertyUpdate, PropertyFilters, 
    PropertySearchParams, PropertyResponse, PropertyType, PropertyStatus
)
from app.db.memory_db import get_properties, get_property, create_property, update_property, delete_property
from app.api.v1.deps import get_current_active_user, get_current_admin, get_current_user_optional
from app.models.user import User
from app.core.config import get_settings
import logging
import time

settings = get_settings()
logger = logging.getLogger(__name__)

router = APIRouter()

# Remove Firestore dependency since we're using memory DB for now

def log_request_info(request: Request):
    """Log information about the incoming request"""
    client = request.client.host if request.client else "unknown"
    method = request.method
    url = str(request.url)
    logger.info(f"Request from {client}: {method} {url}")

@router.get("/", response_model=PropertyResponse)
async def list_properties(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of properties to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of properties to return"),
    property_type: Optional[PropertyType] = Query(None, description="Filter by property type"),
    status: Optional[PropertyStatus] = Query(None, description="Filter by status"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    min_bedrooms: Optional[int] = Query(None, ge=0, description="Minimum bedrooms"),
    max_bedrooms: Optional[int] = Query(None, ge=0, description="Maximum bedrooms"),
    min_bathrooms: Optional[float] = Query(None, ge=0, description="Minimum bathrooms"),
    max_bathrooms: Optional[float] = Query(None, ge=0, description="Maximum bathrooms"),
    min_area: Optional[float] = Query(None, ge=0, description="Minimum area"),
    max_area: Optional[float] = Query(None, ge=0, description="Maximum area"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    zip_code: Optional[str] = Query(None, description="Filter by zip code"),
    has_garage: Optional[bool] = Query(None, description="Filter by garage availability"),
    has_pool: Optional[bool] = Query(None, description="Filter by pool availability"),
    has_garden: Optional[bool] = Query(None, description="Filter by garden availability"),
    pet_friendly: Optional[bool] = Query(None, description="Filter by pet friendliness"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get list of properties with filtering, sorting, and pagination"""
    log_request_info(request)
    start_time = time.time()
    
    try:
        # Create filters object
        filters = PropertyFilters(
            property_type=property_type,
            status=status,
            min_price=min_price,
            max_price=max_price,
            min_bedrooms=min_bedrooms,
            max_bedrooms=max_bedrooms,
            min_bathrooms=min_bathrooms,
            max_bathrooms=max_bathrooms,
            min_area=min_area,
            max_area=max_area,
            city=city,
            state=state,
            zip_code=zip_code,
            has_garage=has_garage,
            has_pool=has_pool,
            has_garden=has_garden,
            pet_friendly=pet_friendly
        )
        
        logger.info(f"Fetching properties with filters: {filters}")
        
        # Use memory database 
        properties = get_properties(
            skip=skip,
            limit=limit,
            property_type=property_type.value if property_type else None,
            min_price=min_price,
            max_price=max_price,
            location=city  # Use city for location filtering
        )
        
        # Convert to Property models
        property_objects = [_convert_to_property_model(prop) for prop in properties]
        
        # For pagination info, we need to get total count without pagination
        all_properties = get_properties(
            skip=0,
            limit=10000,  # Get all for counting
            property_type=property_type.value if property_type else None,
            min_price=min_price,
            max_price=max_price,
            location=city
        )
        total = len(all_properties)
        has_more = skip + limit < total
        
        elapsed = time.time() - start_time
        logger.info(f"Successfully retrieved {len(property_objects)} properties (total: {total}) in {elapsed:.2f}s")
        
        return PropertyResponse(
            properties=property_objects,
            total=total,
            skip=skip,
            limit=limit,
            has_more=has_more
        )
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Error fetching properties after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch properties: {str(e)}"
        )

@router.get("/search", response_model=PropertyResponse)
async def search_properties(
    request: Request,
    q: str = Query(..., description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Search properties by query string"""
    log_request_info(request)
    start_time = time.time()
    
    try:
        logger.info(f"Searching properties with query: '{q}'")
        
        # Get all properties from memory database
        from app.db.memory_db import properties_db
        all_properties = list(properties_db.values())
        
        logger.info(f"Total properties in database: {len(all_properties)}")
        
        # If no query, return all properties
        if not q.strip():
            filtered_properties = all_properties
        else:
            # Search across multiple fields with improved matching
            search_terms = q.lower().split()
            filtered_properties = []
            
            for prop in all_properties:
                match_found = False
                
                # Create searchable text from all relevant fields
                searchable_fields = []
                
                # Add title and description
                searchable_fields.append(prop.get('title', ''))
                searchable_fields.append(prop.get('description', ''))
                searchable_fields.append(prop.get('property_type', ''))
                
                # Add location fields
                location = prop.get('location', {})
                if isinstance(location, dict):
                    searchable_fields.extend([
                        location.get('address', ''),
                        location.get('city', ''),
                        location.get('state', ''),
                        location.get('zip_code', ''),
                        location.get('country', ''),
                        location.get('neighborhood', '')
                    ])
                elif isinstance(location, str):
                    searchable_fields.append(location)
                
                # Add tags
                tags = prop.get('tags', [])
                if isinstance(tags, list):
                    searchable_fields.extend(tags)
                
                # Add features (for properties with pools, garages, etc.)
                features = prop.get('features', {})
                if isinstance(features, dict):
                    for feature_key, feature_value in features.items():
                        if feature_value is True:
                            # Convert snake_case to readable words
                            feature_name = feature_key.replace('has_', '').replace('_', ' ')
                            searchable_fields.append(feature_name)
                
                # Combine all searchable text
                combined_text = ' '.join(str(field) for field in searchable_fields).lower()
                
                # Check if all search terms are found (AND logic)
                if all(term in combined_text for term in search_terms):
                    match_found = True
                
                if match_found:
                    filtered_properties.append(prop)
        
        logger.info(f"Found {len(filtered_properties)} properties matching query: '{q}'")
        
        # Apply pagination
        total = len(filtered_properties)
        paginated_properties = filtered_properties[skip:skip + limit]
        has_more = skip + limit < total
        
        # Convert to Property models
        property_objects = [_convert_to_property_model(prop) for prop in paginated_properties]
        
        elapsed = time.time() - start_time
        logger.info(f"Found {len(property_objects)} properties matching query: '{q}' in {elapsed:.2f}s")
        
        return PropertyResponse(
            properties=property_objects,
            total=total,
            skip=skip,
            limit=limit,
            has_more=has_more
        )
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Error searching properties with query '{q}' after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search properties: {str(e)}"
        )

@router.get("/{property_id}", response_model=Property)
async def get_property_endpoint(
    property_id: str,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Get a specific property by ID"""
    log_request_info(request)
    start_time = time.time()
    
    try:
        logger.info(f"Fetching property with ID: {property_id}")
        
        property_data = get_property(property_id)
        
        elapsed = time.time() - start_time
        if not property_data:
            logger.warning(f"Property not found with ID: {property_id} after {elapsed:.2f}s")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Property with ID {property_id} not found"
            )
        
        property_obj = _convert_to_property_model(property_data)
        
        logger.info(f"Successfully retrieved property: {property_id} in {elapsed:.2f}s")
        return property_obj
        
    except HTTPException:
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Error fetching property {property_id} after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch property: {str(e)}"
        )

@router.post("/", response_model=Property, status_code=status.HTTP_201_CREATED)
async def create_property_endpoint(
    property_data: PropertyCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    """Create a new property (requires authentication)"""
    log_request_info(request)
    start_time = time.time()
    
    try:
        logger.info(f"Creating new property: {property_data.title}")
        
        # Add agent_id from current user if not specified
        if not property_data.agent_id:
            property_data.agent_id = str(current_user.id)
        
        # Convert to dict for Firestore
        property_dict = property_data.dict()
        
        new_property = create_property(property_dict)
        
        elapsed = time.time() - start_time
        logger.info(f"Successfully created property with ID: {new_property['id']} in {elapsed:.2f}s")
        
        property_obj = _convert_to_property_model(new_property)
        return property_obj
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Error creating property after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create property: {str(e)}"
        )

@router.put("/{property_id}", response_model=Property)
async def update_property_endpoint(
    property_id: str,
    property_update: PropertyUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    """Update a property (requires authentication)"""
    log_request_info(request)
    start_time = time.time()
    
    try:
        # Check if property exists and user has permission
        existing_property = get_property(property_id)
        if not existing_property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Property with ID {property_id} not found"
            )
        
        # Check if user is admin or property agent
        if (current_user.role.value != "admin" and 
            existing_property.get("agent_id") != str(current_user.id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this property"
            )
        
        update_data = {k: v for k, v in property_update.dict().items() if v is not None}
        logger.info(f"Updating property with ID: {property_id}")
        
        updated_property = update_property(property_id, update_data)
        
        elapsed = time.time() - start_time
        if not updated_property:
            logger.warning(f"Property not found for update with ID: {property_id} after {elapsed:.2f}s")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Property with ID {property_id} not found"
            )
        
        property_obj = _convert_to_property_model(updated_property)
        
        logger.info(f"Successfully updated property: {property_id} in {elapsed:.2f}s")
        return property_obj
        
    except HTTPException:
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Error updating property {property_id} after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update property: {str(e)}"
        )

@router.delete("/{property_id}")
async def delete_property_endpoint(
    property_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    """Delete a property (requires authentication)"""
    log_request_info(request)
    start_time = time.time()
    
    try:
        # Check if property exists and user has permission
        existing_property = get_property(property_id)
        if not existing_property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Property with ID {property_id} not found"
            )
        
        # Check if user is admin or property agent
        if (current_user.role.value != "admin" and 
            existing_property.get("agent_id") != str(current_user.id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this property"
            )
        
        logger.info(f"Deleting property with ID: {property_id}")
        success = delete_property(property_id)
        
        elapsed = time.time() - start_time
        if not success:
            logger.warning(f"Property not found for deletion with ID: {property_id} after {elapsed:.2f}s")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Property with ID {property_id} not found"
            )
        
        logger.info(f"Successfully deleted property: {property_id} in {elapsed:.2f}s")
        return {"message": "Property deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Error deleting property {property_id} after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete property: {str(e)}"
        )

# Admin-only endpoints
@router.get("/admin/stats", response_model=Dict[str, Any])
async def get_property_stats(
    current_user: User = Depends(get_current_admin),
):
    """Get property statistics (admin only)"""
    try:
        # Get all properties from memory database
        properties = get_properties(skip=0, limit=10000)
        
        total_properties = len(properties)
        available_properties = len([p for p in properties if p.get('status') == 'available'])
        sold_properties = len([p for p in properties if p.get('status') == 'sold'])
        rented_properties = len([p for p in properties if p.get('status') == 'rented'])
        
        total_value = sum(p.get('price', 0) for p in properties)
        avg_price = total_value / total_properties if total_properties > 0 else 0
        
        return {
            "total_properties": total_properties,
            "available_properties": available_properties,
            "sold_properties": sold_properties,
            "rented_properties": rented_properties,
            "total_value": total_value,
            "average_price": avg_price
        }
    except Exception as e:
        logger.error(f"Error getting property stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get property statistics: {str(e)}"
        )

# Helper functions
def _apply_filters(properties: List[Dict], filters: PropertyFilters) -> List[Dict]:
    """Apply filters to property list"""
    filtered = properties
    
    if filters.property_type:
        filtered = [p for p in filtered if p.get('property_type') == filters.property_type.value]
    
    if filters.status:
        filtered = [p for p in filtered if p.get('status') == filters.status.value]
    
    if filters.min_price is not None:
        filtered = [p for p in filtered if p.get('price', 0) >= filters.min_price]
    
    if filters.max_price is not None:
        filtered = [p for p in filtered if p.get('price', 0) <= filters.max_price]
    
    if filters.min_bedrooms is not None:
        filtered = [p for p in filtered if p.get('bedrooms', 0) >= filters.min_bedrooms]
    
    if filters.max_bedrooms is not None:
        filtered = [p for p in filtered if p.get('bedrooms', 0) <= filters.max_bedrooms]
    
    if filters.min_bathrooms is not None:
        filtered = [p for p in filtered if p.get('bathrooms', 0) >= filters.min_bathrooms]
    
    if filters.max_bathrooms is not None:
        filtered = [p for p in filtered if p.get('bathrooms', 0) <= filters.max_bathrooms]
    
    if filters.min_area is not None:
        filtered = [p for p in filtered if p.get('area', 0) >= filters.min_area]
    
    if filters.max_area is not None:
        filtered = [p for p in filtered if p.get('area', 0) <= filters.max_area]
    
    if filters.city:
        filtered = [p for p in filtered if 
                   filters.city.lower() in p.get('location', {}).get('city', '').lower()]
    
    if filters.state:
        filtered = [p for p in filtered if 
                   filters.state.lower() in p.get('location', {}).get('state', '').lower()]
    
    return filtered

def _apply_sorting(properties: List[Dict], sort_by: str, sort_order: str) -> List[Dict]:
    """Apply sorting to property list"""
    reverse = sort_order == "desc"
    
    try:
        return sorted(properties, key=lambda x: x.get(sort_by, 0), reverse=reverse)
    except Exception:
        # Fallback to created_at if sort field doesn't exist
        return sorted(properties, key=lambda x: x.get('created_at', 0), reverse=True)

def _convert_to_property_model(property_data: Dict) -> Property:
    """Convert dictionary to Property model"""
    try:
        # Handle timestamp conversion
        if 'created_at' in property_data and hasattr(property_data['created_at'], 'isoformat'):
            property_data['created_at'] = property_data['created_at'].isoformat()
        if 'updated_at' in property_data and hasattr(property_data['updated_at'], 'isoformat'):
            property_data['updated_at'] = property_data['updated_at'].isoformat()
        
        # Ensure required fields have defaults for backward compatibility
        if 'location' not in property_data or isinstance(property_data['location'], str):
            # Handle legacy location format
            location_str = property_data.get('location', '')
            property_data['location'] = {
                'address': location_str,
                'city': '',
                'state': '',
                'zip_code': '',
                'country': 'US'
            }
        
        if 'features' not in property_data:
            property_data['features'] = {}
        
        if 'media' not in property_data:
            # Handle legacy images field
            images = property_data.get('images', [])
            property_data['media'] = {'images': images}
        
        return Property(**property_data)
    except Exception as e:
        logger.error(f"Error converting property data to model: {str(e)}")
        # Return a basic property model as fallback
        return Property(
            id=property_data.get('id', ''),
            title=property_data.get('title', 'Unknown'),
            description=property_data.get('description', ''),
            price=property_data.get('price', 0),
            location={'address': property_data.get('location', ''), 'city': '', 'state': '', 'zip_code': '', 'country': 'US'},
            property_type=property_data.get('property_type', 'house'),
            bedrooms=property_data.get('bedrooms', 0),
            bathrooms=property_data.get('bathrooms', 0),
            area=property_data.get('area', 0),
            features={},
            media={'images': property_data.get('images', [])},
            status=property_data.get('status', 'available')
        )