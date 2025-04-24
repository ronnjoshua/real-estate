from typing import List, Optional, Dict, Any
from firebase_admin import firestore
from ..core.firebase import get_firebase_app
import logging
import uuid
import json
import datetime

logger = logging.getLogger(__name__)

def convert_timestamps(data):
    """Convert Firestore timestamp objects to ISO format strings."""
    if isinstance(data, dict):
        for key, value in data.items():
            if hasattr(value, 'seconds') and hasattr(value, 'nanos'):
                # This is likely a Firestore timestamp
                try:
                    data[key] = value.isoformat()
                except AttributeError:
                    data[key] = str(value)
            elif isinstance(value, dict):
                convert_timestamps(value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        convert_timestamps(item)
    return data

class FirestoreService:
    def __init__(self):
        try:
            firebase_app = get_firebase_app()
            if firebase_app == "mock_app":
                # Mock implementation for development
                self.is_mock = True
                self.mock_properties = self._create_mock_properties()
                logger.warning("Using mock Firestore implementation with sample properties")
            else:
                self.is_mock = False
                self.db = firestore.client(firebase_app)
                self.properties_collection = self.db.collection('properties')
                logger.info("Initialized Firestore with collection: properties")
        except Exception as e:
            logger.error(f"Error initializing Firestore: {e}")
            # Fallback to mock implementation
            self.is_mock = True
            self.mock_properties = self._create_mock_properties()
            logger.warning("Falling back to mock Firestore implementation with sample properties")

    def _create_mock_properties(self) -> List[Dict[str, Any]]:
        """Create sample properties for development."""
        return [
            {
                "id": "1",  # Use string IDs that match what's in Firestore
                "title": "Luxury Waterfront Villa",
                "description": "Stunning 4-bedroom villa with panoramic ocean views, private pool, and modern amenities.",
                "price": 1200000,
                "location": "Miami Beach, FL",
                "bedrooms": 4,
                "bathrooms": 3.5,
                "area": 3500,
                "images": [
                    "https://images.unsplash.com/photo-1613490493576-7fde63acd811?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1000&q=80",
                    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1000&q=80"
                ],
                "property_type": "Luxury",
                "status": "available",
                "created_at": "2024-03-20T00:00:00Z",
                "updated_at": "2024-03-20T00:00:00Z"
            },
            {
                "id": "2",
                "title": "Modern Downtown Penthouse",
                "description": "Exclusive penthouse with city views, featuring high-end finishes and a private terrace.",
                "price": 850000,
                "location": "Los Angeles, CA",
                "bedrooms": 3,
                "bathrooms": 2,
                "area": 2200,
                "images": [
                    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1000&q=80"
                ],
                "property_type": "Penthouse",
                "status": "available",
                "created_at": "2024-03-20T00:00:00Z",
                "updated_at": "2024-03-20T00:00:00Z"
            },
            {
                "id": "3",
                "title": "Cozy Mountain Cabin",
                "description": "Charming cabin with mountain views, a fireplace, and rustic decor.",
                "price": 450000,
                "location": "Aspen, CO",
                "bedrooms": 2,
                "bathrooms": 1.5,
                "area": 1200,
                "images": [
                    "https://images.unsplash.com/photo-1516402707554-0a25b1921143?auto=format&fit=crop&w=1000&q=80"
                ],
                "property_type": "Cabin",
                "status": "pending",
                "created_at": "2024-03-20T00:00:00Z",
                "updated_at": "2024-03-20T00:00:00Z"
            }
        ]

    async def get_all_properties(self) -> List[Dict[str, Any]]:
        """Fetch all properties from Firestore."""
        logger.info("Fetching all properties")
        
        if self.is_mock:
            logger.info(f"Using mock data: {len(self.mock_properties)} properties found")
            return self.mock_properties
            
        properties = []
        try:
            logger.info("Querying Firestore properties collection")
            docs = self.properties_collection.stream()
            for doc in docs:
                property_data = doc.to_dict()
                property_data['id'] = doc.id
                # Convert any timestamp objects
                convert_timestamps(property_data)
                properties.append(property_data)
            
            logger.info(f"Fetched {len(properties)} properties from Firestore")
        except Exception as e:
            logger.error(f"Error fetching properties: {e}", exc_info=True)
        
        return properties

    async def get_property_by_id(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single property by ID."""
        logger.info(f"Fetching property with ID: {property_id}")
        
        if self.is_mock:
            # Try exact match first
            for prop in self.mock_properties:
                if prop.get('id') == property_id:
                    logger.info(f"Found mock property with ID: {property_id}")
                    return prop
                    
            # Try with different ID formats if it's a number
            if property_id.isdigit():
                for prop in self.mock_properties:
                    if prop.get('id') == property_id or prop.get('id') == int(property_id):
                        logger.info(f"Found mock property with numeric ID: {property_id}")
                        return prop
                        
            logger.warning(f"No mock property found with ID: {property_id}")
            return None
            
        try:
            logger.info(f"Querying Firestore for property with ID: {property_id}")
            
            # Try with the original ID
            doc = self.properties_collection.document(property_id).get()
            
            # If not found and ID is numeric, try a query to find by field
            if not doc.exists and property_id.isdigit():
                logger.info(f"Document not found, trying query for ID field: {property_id}")
                query = self.properties_collection.where('id', '==', property_id)
                results = query.stream()
                
                for result in results:
                    property_data = result.to_dict()
                    property_data['id'] = result.id
                    logger.info(f"Found property with ID field: {property_id}")
                    convert_timestamps(property_data)
                    return property_data
            
            if doc.exists:
                property_data = doc.to_dict()
                property_data['id'] = doc.id
                logger.info(f"Found property with ID: {property_id}")
                convert_timestamps(property_data)
                return property_data
            else:
                logger.warning(f"No property found in Firestore with ID: {property_id}")
        except Exception as e:
            logger.error(f"Error fetching property {property_id}: {e}", exc_info=True)
        
        return None

    async def create_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new property in Firestore."""
        logger.info(f"Creating new property: {property_data.get('title', 'Untitled')}")
        
        if self.is_mock:
            # Generate a mock ID if not provided
            if 'id' not in property_data:
                property_data['id'] = str(len(self.mock_properties) + 1)
            self.mock_properties.append(property_data)
            logger.info(f"Created mock property with ID: {property_data['id']}")
            return property_data
            
        try:
            logger.info("Adding property to Firestore")
            # Set created_at and updated_at timestamps
            now = firestore.SERVER_TIMESTAMP
            property_data['created_at'] = now
            property_data['updated_at'] = now
            
            # Check if ID is provided
            if 'id' in property_data:
                provided_id = property_data.pop('id')
                doc_ref = self.properties_collection.document(provided_id)
                doc_ref.set(property_data)
                property_data['id'] = provided_id
            else:
                doc_ref = self.properties_collection.document()
                doc_ref.set(property_data)
                property_data['id'] = doc_ref.id
                
            # Replace SERVER_TIMESTAMP with current time for the response
            if property_data['created_at'] == now:
                property_data['created_at'] = datetime.datetime.now().isoformat()
            if property_data['updated_at'] == now:
                property_data['updated_at'] = datetime.datetime.now().isoformat()
                
            logger.info(f"Successfully created property with ID: {property_data['id']}")
            return property_data
        except Exception as e:
            logger.error(f"Error creating property: {e}", exc_info=True)
            raise

    async def update_property(self, property_id: str, property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing property."""
        logger.info(f"Updating property with ID: {property_id}")
        
        if self.is_mock:
            for i, prop in enumerate(self.mock_properties):
                if prop.get('id') == property_id:
                    self.mock_properties[i].update(property_data)
                    # Ensure ID is preserved
                    self.mock_properties[i]['id'] = property_id
                    # Update timestamp
                    self.mock_properties[i]['updated_at'] = datetime.datetime.now().isoformat()
                    logger.info(f"Updated mock property with ID: {property_id}")
                    return self.mock_properties[i]
            logger.warning(f"No mock property found with ID: {property_id} for update")
            return None
            
        try:
            logger.info(f"Updating property in Firestore with ID: {property_id}")
            # Set updated_at timestamp
            property_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.properties_collection.document(property_id)
            if doc_ref.get().exists:
                doc_ref.update(property_data)
                updated_doc = doc_ref.get()
                updated_data = updated_doc.to_dict()
                updated_data['id'] = property_id
                
                # Convert timestamps for the response
                convert_timestamps(updated_data)
                
                logger.info(f"Successfully updated property with ID: {property_id}")
                return updated_data
            else:
                logger.warning(f"No property found in Firestore with ID: {property_id} for update")
        except Exception as e:
            logger.error(f"Error updating property {property_id}: {e}", exc_info=True)
        
        return None

    async def delete_property(self, property_id: str) -> bool:
        """Delete a property."""
        logger.info(f"Deleting property with ID: {property_id}")
        
        if self.is_mock:
            for i, prop in enumerate(self.mock_properties):
                if prop.get('id') == property_id:
                    del self.mock_properties[i]
                    logger.info(f"Deleted mock property with ID: {property_id}")
                    return True
            logger.warning(f"No mock property found with ID: {property_id} for deletion")
            return False
            
        try:
            logger.info(f"Deleting property from Firestore with ID: {property_id}")
            doc_ref = self.properties_collection.document(property_id)
            if doc_ref.get().exists:
                doc_ref.delete()
                logger.info(f"Successfully deleted property with ID: {property_id}")
                return True
            else:
                logger.warning(f"No property found in Firestore with ID: {property_id} for deletion")
        except Exception as e:
            logger.error(f"Error deleting property {property_id}: {e}", exc_info=True)
        
        return False

    async def search_properties(self, query: str) -> List[Dict[str, Any]]:
        """Search properties based on title, description, or location."""
        logger.info(f"Searching properties with query: '{query}'")
        
        if self.is_mock:
            results = [
                prop for prop in self.mock_properties
                if query.lower() in prop.get('title', '').lower() or
                   query.lower() in prop.get('description', '').lower() or
                   query.lower() in prop.get('location', '').lower()
            ]
            logger.info(f"Found {len(results)} mock properties matching query: '{query}'")
            return results
            
        properties = []
        try:
            # Convert query to lowercase for case-insensitive search
            query = query.lower()
            logger.info(f"Performing case-insensitive search in Firestore for: '{query}'")
            
            # Get all properties (in a production environment, you'd want to implement proper indexing)
            docs = self.properties_collection.stream()
            
            for doc in docs:
                data = doc.to_dict()
                # Check if query matches any of the searchable fields
                if (query in data.get('title', '').lower() or
                    query in data.get('description', '').lower() or
                    query in data.get('location', '').lower()):
                    data['id'] = doc.id
                    # Convert timestamps
                    convert_timestamps(data)
                    properties.append(data)
            
            logger.info(f"Found {len(properties)} properties matching query: '{query}' in Firestore")
        except Exception as e:
            logger.error(f"Error searching properties: {e}", exc_info=True)
            
        return properties 