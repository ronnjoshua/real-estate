from typing import List, Optional
from ..core.firebase import db
from ..models.property import Property, PropertyCreate, PropertyUpdate

class PropertyService:
    def __init__(self):
        self.collection = db.collection('properties')

    async def create_property(self, property_data: PropertyCreate) -> Property:
        doc_ref = self.collection.document()
        property_dict = property_data.model_dump()
        property_dict['id'] = doc_ref.id
        doc_ref.set(property_dict)
        return Property(**property_dict)

    async def get_property(self, property_id: str) -> Optional[Property]:
        doc = self.collection.document(property_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return Property(**data)
        return None

    async def list_properties(
        self,
        skip: int = 0,
        limit: int = 10,
        property_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        location: Optional[str] = None
    ) -> List[Property]:
        query = self.collection
        
        if property_type:
            query = query.where('property_type', '==', property_type)
        if min_price is not None:
            query = query.where('price', '>=', min_price)
        if max_price is not None:
            query = query.where('price', '<=', max_price)
        if location:
            query = query.where('location', '==', location)
            
        docs = query.limit(limit).offset(skip).stream()
        return [Property(**doc.to_dict(), id=doc.id) for doc in docs]

    async def update_property(self, property_id: str, property_data: PropertyUpdate) -> Optional[Property]:
        doc_ref = self.collection.document(property_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
            
        update_data = property_data.model_dump(exclude_unset=True)
        update_data['updated_at'] = property_data.updated_at
        
        doc_ref.update(update_data)
        updated_doc = doc_ref.get()
        data = updated_doc.to_dict()
        data['id'] = updated_doc.id
        return Property(**data)

    async def delete_property(self, property_id: str) -> bool:
        doc_ref = self.collection.document(property_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
            
        doc_ref.delete()
        return True 