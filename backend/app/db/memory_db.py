from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from app.models.user import User, UserInDB, Invitation, UserRole
from app.core.security import get_password_hash

# In-memory storage
properties_db: Dict[str, Dict[str, Any]] = {}
users_db: Dict[str, UserInDB] = {}
invitations_db: Dict[str, Invitation] = {}

# Property management functions
def get_properties(
    skip: int = 0,
    limit: int = 10,
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    location: Optional[str] = None
) -> List[Dict[str, Any]]:
    filtered_properties = list(properties_db.values())
    
    if property_type:
        filtered_properties = [p for p in filtered_properties if p['property_type'] == property_type]
    if min_price is not None:
        filtered_properties = [p for p in filtered_properties if p['price'] >= min_price]
    if max_price is not None:
        filtered_properties = [p for p in filtered_properties if p['price'] <= max_price]
    if location:
        filtered_properties = [p for p in filtered_properties if location.lower() in p['location'].lower()]
    
    return filtered_properties[skip:skip + limit]

def get_property(property_id: str) -> Optional[Dict[str, Any]]:
    return properties_db.get(property_id)

def create_property(property_data: Dict[str, Any]) -> Dict[str, Any]:
    property_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    property_data.update({
        'id': property_id,
        'created_at': now,
        'updated_at': now
    })
    
    properties_db[property_id] = property_data
    return property_data

def update_property(property_id: str, property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if property_id not in properties_db:
        return None
    
    property_data['updated_at'] = datetime.utcnow().isoformat()
    properties_db[property_id].update(property_data)
    return properties_db[property_id]

def delete_property(property_id: str) -> bool:
    if property_id not in properties_db:
        return False
    
    del properties_db[property_id]
    return True

# User management functions
def get_user_by_email(email: str) -> Optional[UserInDB]:
    for user in users_db.values():
        if user.email == email:
            return user
    return None

def create_user(
    email: str,
    full_name: str,
    hashed_password: str,
    role: str
) -> UserInDB:
    user_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    user = UserInDB(
        id=user_id,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        role=role,
        is_active=True,
        created_at=now,
        updated_at=now
    )
    
    users_db[user_id] = user
    return user

def update_user(email: str, updates: dict) -> Optional[UserInDB]:
    user = get_user_by_email(email)
    if not user:
        return None

    # Update user fields
    if updates.get("full_name"):
        user.full_name = updates["full_name"]
    if updates.get("email"):
        user.email = updates["email"]
    if updates.get("hashed_password"):
        user.hashed_password = updates["hashed_password"]
    
    user.updated_at = datetime.utcnow()
    
    # Update the user in the database
    users_db[user.id] = user
    return user

# Invitation management functions
def create_invitation(
    email: str,
    role: str,
    token: str,
    expires_at: Optional[datetime] = None
) -> Invitation:
    invitation_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    invitation = Invitation(
        id=invitation_id,
        email=email,
        role=role,
        token=token,
        created_at=now,
        expires_at=expires_at,
        is_used=False
    )
    
    invitations_db[invitation_id] = invitation
    return invitation

def get_invitation_by_token(token: str) -> Optional[Invitation]:
    for invitation in invitations_db.values():
        if invitation.token == token:
            return invitation
    return None

def mark_invitation_as_used(token: str) -> bool:
    for invitation in invitations_db.values():
        if invitation.token == token:
            invitation.is_used = True
            return True
    return False

def create_initial_admin():
    # Check if admin exists
    for user in users_db.values():
        if user.role == UserRole.ADMIN:
            return
    
    # Create admin user if none exists
    admin_email = "admin@realestate.com"
    admin_password = "admin123"  # This is just for testing, should be changed in production
    
    if not get_user_by_email(admin_email):
        create_user(
            email=admin_email,
            full_name="Admin User",
            hashed_password=get_password_hash(admin_password),
            role=UserRole.ADMIN
        )

# Create initial admin user when the module is loaded
create_initial_admin() 