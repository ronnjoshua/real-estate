from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class PropertyModel(Base):
    __tablename__ = "properties"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    property_type = Column(String(50), nullable=False, default="house")
    bedrooms = Column(Integer, nullable=False, default=0)
    bathrooms = Column(Integer, nullable=False, default=0)
    area = Column(Float, nullable=False, default=0)
    status = Column(String(50), nullable=False, default="available")

    # Store location as JSON
    location = Column(JSON, nullable=True)

    # Store features as JSON
    features = Column(JSON, nullable=True)

    # Store media as JSON
    media = Column(JSON, nullable=True)

    # Store tags as JSON array
    tags = Column(JSON, nullable=True)

    agent_id = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "property_type": self.property_type,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "area": self.area,
            "status": self.status,
            "location": self.location or {},
            "features": self.features or {},
            "media": self.media or {"images": [], "documents": []},
            "tags": self.tags or [],
            "agent_id": self.agent_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="client")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class InvitationModel(Base):
    __tablename__ = "invitations"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="client")
    token = Column(String(255), unique=True, nullable=False, index=True)
    is_used = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
