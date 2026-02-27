from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging
from app.models.user import UserInDB, Invitation, UserRole
from app.core.security import get_password_hash
from app.db.database import SessionLocal, init_db
from app.db.models import PropertyModel, UserModel, InvitationModel

logger = logging.getLogger(__name__)


def get_session():
    """Get a database session"""
    if SessionLocal is None:
        return None
    return SessionLocal()


# Property management functions
def get_properties(
    skip: int = 0,
    limit: int = 10,
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    location: Optional[str] = None
) -> List[Dict[str, Any]]:
    session = get_session()
    if session is None:
        return []

    try:
        query = session.query(PropertyModel)

        if property_type:
            query = query.filter(PropertyModel.property_type == property_type)
        if min_price is not None:
            query = query.filter(PropertyModel.price >= min_price)
        if max_price is not None:
            query = query.filter(PropertyModel.price <= max_price)
        if location:
            # Search in location JSON field
            query = query.filter(
                PropertyModel.location['city'].astext.ilike(f'%{location}%')
            )

        query = query.order_by(PropertyModel.created_at.desc())
        properties = query.offset(skip).limit(limit).all()

        return [p.to_dict() for p in properties]
    except Exception as e:
        logger.error(f"Error getting properties: {e}")
        return []
    finally:
        session.close()


def get_all_properties_count() -> int:
    """Get total count of properties"""
    session = get_session()
    if session is None:
        return 0

    try:
        return session.query(PropertyModel).count()
    except Exception as e:
        logger.error(f"Error getting property count: {e}")
        return 0
    finally:
        session.close()


def get_property(property_id: str) -> Optional[Dict[str, Any]]:
    session = get_session()
    if session is None:
        return None

    try:
        property_obj = session.query(PropertyModel).filter(PropertyModel.id == property_id).first()
        return property_obj.to_dict() if property_obj else None
    except Exception as e:
        logger.error(f"Error getting property: {e}")
        return None
    finally:
        session.close()


def create_property(property_data: Dict[str, Any]) -> Dict[str, Any]:
    session = get_session()
    if session is None:
        raise Exception("Database not configured")

    try:
        property_obj = PropertyModel(
            id=str(uuid.uuid4()),
            title=property_data.get('title', ''),
            description=property_data.get('description', ''),
            price=property_data.get('price', 0),
            property_type=property_data.get('property_type', 'house'),
            bedrooms=property_data.get('bedrooms', 0),
            bathrooms=property_data.get('bathrooms', 0),
            area=property_data.get('area', 0),
            status=property_data.get('status', 'available'),
            location=property_data.get('location', {}),
            features=property_data.get('features', {}),
            media=property_data.get('media', {'images': [], 'documents': []}),
            tags=property_data.get('tags', []),
            agent_id=property_data.get('agent_id', '')
        )

        session.add(property_obj)
        session.commit()
        session.refresh(property_obj)

        return property_obj.to_dict()
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating property: {e}")
        raise
    finally:
        session.close()


def update_property(property_id: str, property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    session = get_session()
    if session is None:
        return None

    try:
        property_obj = session.query(PropertyModel).filter(PropertyModel.id == property_id).first()
        if not property_obj:
            return None

        # Update fields
        for key, value in property_data.items():
            if hasattr(property_obj, key) and key not in ['id', 'created_at']:
                setattr(property_obj, key, value)

        session.commit()
        session.refresh(property_obj)

        return property_obj.to_dict()
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating property: {e}")
        return None
    finally:
        session.close()


def delete_property(property_id: str) -> bool:
    session = get_session()
    if session is None:
        return False

    try:
        property_obj = session.query(PropertyModel).filter(PropertyModel.id == property_id).first()
        if not property_obj:
            return False

        session.delete(property_obj)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting property: {e}")
        return False
    finally:
        session.close()


# User management functions
def get_user_by_email(email: str) -> Optional[UserInDB]:
    session = get_session()
    if session is None:
        return None

    try:
        user = session.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            return None

        return UserInDB(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None
    finally:
        session.close()


def create_user(
    email: str,
    full_name: str,
    hashed_password: str,
    role: str
) -> UserInDB:
    session = get_session()
    if session is None:
        raise Exception("Database not configured")

    try:
        user = UserModel(
            id=str(uuid.uuid4()),
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=role,
            is_active=True
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return UserInDB(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating user: {e}")
        raise
    finally:
        session.close()


def update_user(email: str, updates: dict) -> Optional[UserInDB]:
    session = get_session()
    if session is None:
        return None

    try:
        user = session.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            return None

        if updates.get("full_name"):
            user.full_name = updates["full_name"]
        if updates.get("email"):
            user.email = updates["email"]
        if updates.get("hashed_password"):
            user.hashed_password = updates["hashed_password"]

        session.commit()
        session.refresh(user)

        return UserInDB(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating user: {e}")
        return None
    finally:
        session.close()


# Invitation management functions
def create_invitation(
    email: str,
    role: str,
    token: str,
    expires_at: Optional[datetime] = None
) -> Invitation:
    session = get_session()
    if session is None:
        raise Exception("Database not configured")

    try:
        invitation = InvitationModel(
            id=str(uuid.uuid4()),
            email=email,
            role=role,
            token=token,
            is_used=False,
            expires_at=expires_at
        )

        session.add(invitation)
        session.commit()
        session.refresh(invitation)

        return Invitation(
            id=invitation.id,
            email=invitation.email,
            role=invitation.role,
            token=invitation.token,
            created_at=invitation.created_at,
            expires_at=invitation.expires_at,
            is_used=invitation.is_used
        )
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating invitation: {e}")
        raise
    finally:
        session.close()


def get_invitation_by_token(token: str) -> Optional[Invitation]:
    session = get_session()
    if session is None:
        return None

    try:
        invitation = session.query(InvitationModel).filter(InvitationModel.token == token).first()
        if not invitation:
            return None

        return Invitation(
            id=invitation.id,
            email=invitation.email,
            role=invitation.role,
            token=invitation.token,
            created_at=invitation.created_at,
            expires_at=invitation.expires_at,
            is_used=invitation.is_used
        )
    except Exception as e:
        logger.error(f"Error getting invitation by token: {e}")
        return None
    finally:
        session.close()


def mark_invitation_as_used(token: str) -> bool:
    session = get_session()
    if session is None:
        return False

    try:
        invitation = session.query(InvitationModel).filter(InvitationModel.token == token).first()
        if not invitation:
            return False

        invitation.is_used = True
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Error marking invitation as used: {e}")
        return False
    finally:
        session.close()


def get_all_invitations() -> List[Invitation]:
    session = get_session()
    if session is None:
        return []

    try:
        invitations = session.query(InvitationModel).all()
        return [
            Invitation(
                id=inv.id,
                email=inv.email,
                role=inv.role,
                token=inv.token,
                created_at=inv.created_at,
                expires_at=inv.expires_at,
                is_used=inv.is_used
            )
            for inv in invitations
        ]
    except Exception as e:
        logger.error(f"Error getting invitations: {e}")
        return []
    finally:
        session.close()


def create_initial_admin():
    """Create initial admin user if none exists"""
    session = get_session()
    if session is None:
        logger.warning("Cannot create initial admin - database not configured")
        return

    try:
        # Check if any admin exists
        admin = session.query(UserModel).filter(UserModel.role == UserRole.ADMIN).first()
        if admin:
            logger.info("Admin user already exists")
            return

        # Create admin user
        admin_email = "admin@realestate.com"
        admin_password = "admin123"

        # Check if this specific admin already exists
        existing = session.query(UserModel).filter(UserModel.email == admin_email).first()
        if existing:
            logger.info("Admin user already exists")
            return

        admin_user = UserModel(
            id=str(uuid.uuid4()),
            email=admin_email,
            full_name="Admin User",
            hashed_password=get_password_hash(admin_password),
            role=UserRole.ADMIN,
            is_active=True
        )

        session.add(admin_user)
        session.commit()
        logger.info(f"Created initial admin user: {admin_email}")
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating initial admin: {e}")
    finally:
        session.close()


def create_sample_properties():
    """Create sample properties - only if database is empty"""
    session = get_session()
    if session is None:
        return

    try:
        # Check if we already have properties
        count = session.query(PropertyModel).count()
        if count > 0:
            logger.info(f"Database already has {count} properties, skipping sample data")
            return

        logger.info("Creating sample properties...")
        sample_properties = [
            {
                "title": "Modern Downtown Apartment",
                "description": "A beautiful 2-bedroom apartment in the heart of downtown with stunning city views.",
                "price": 450000,
                "location": {
                    "address": "123 Main St",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip_code": "94102",
                    "country": "US"
                },
                "property_type": "apartment",
                "bedrooms": 2,
                "bathrooms": 2,
                "area": 1200,
                "features": {
                    "has_garage": True,
                    "has_pool": False,
                    "has_garden": False,
                    "has_balcony": True,
                    "pet_friendly": True
                },
                "media": {
                    "images": ["https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=400"],
                    "documents": []
                },
                "status": "available",
                "tags": ["downtown", "modern", "city-view"]
            },
            {
                "title": "Family House with Garden",
                "description": "Spacious 4-bedroom house perfect for families, featuring a large garden and garage.",
                "price": 750000,
                "location": {
                    "address": "456 Oak Ave",
                    "city": "Oakland",
                    "state": "CA",
                    "zip_code": "94610",
                    "country": "US"
                },
                "property_type": "house",
                "bedrooms": 4,
                "bathrooms": 3,
                "area": 2500,
                "features": {
                    "has_garage": True,
                    "has_pool": True,
                    "has_garden": True,
                    "has_balcony": False,
                    "pet_friendly": True
                },
                "media": {
                    "images": ["https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400"],
                    "documents": []
                },
                "status": "available",
                "tags": ["family", "garden", "spacious"]
            },
            {
                "title": "Luxury Condo with Pool",
                "description": "High-end 3-bedroom condo with pool access and premium amenities.",
                "price": 680000,
                "location": {
                    "address": "789 Pine St",
                    "city": "Berkeley",
                    "state": "CA",
                    "zip_code": "94704",
                    "country": "US"
                },
                "property_type": "condo",
                "bedrooms": 3,
                "bathrooms": 2,
                "area": 1800,
                "features": {
                    "has_garage": True,
                    "has_pool": True,
                    "has_garden": False,
                    "has_balcony": True,
                    "pet_friendly": False
                },
                "media": {
                    "images": ["https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400"],
                    "documents": []
                },
                "status": "available",
                "tags": ["luxury", "amenities", "pool"]
            }
        ]

        for prop_data in sample_properties:
            prop = PropertyModel(
                id=str(uuid.uuid4()),
                title=prop_data['title'],
                description=prop_data['description'],
                price=prop_data['price'],
                property_type=prop_data['property_type'],
                bedrooms=prop_data['bedrooms'],
                bathrooms=prop_data['bathrooms'],
                area=prop_data['area'],
                status=prop_data['status'],
                location=prop_data['location'],
                features=prop_data['features'],
                media=prop_data['media'],
                tags=prop_data['tags']
            )
            session.add(prop)

        session.commit()
        logger.info("Sample properties created successfully")
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating sample properties: {e}")
    finally:
        session.close()


def initialize_database():
    """Initialize the database with tables and initial data"""
    logger.info("Initializing database...")

    # Create tables
    if init_db():
        # Create initial admin
        create_initial_admin()
        # Create sample properties only if empty
        create_sample_properties()
        logger.info("Database initialization complete")
    else:
        logger.error("Failed to initialize database")
