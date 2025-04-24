from app.db.memory_db import create_user, create_property
from app.core.security import get_password_hash
from app.models.user import UserRole

def init_db():
    # Create admin user
    admin_email = "admin@realestate.com"
    admin_password = "admin123"
    
    create_user(
        email=admin_email,
        full_name="Admin User",
        hashed_password=get_password_hash(admin_password),
        role=UserRole.ADMIN
    )
    
    # Create some test properties
    test_properties = [
        {
            "title": "Modern Downtown Apartment",
            "description": "Beautiful modern apartment in the heart of downtown",
            "price": 500000,
            "property_type": "apartment",
            "location": "Downtown",
            "bedrooms": 2,
            "bathrooms": 2,
            "area": 1200,
            "status": "active"
        },
        {
            "title": "Suburban Family Home",
            "description": "Spacious family home with a large backyard",
            "price": 750000,
            "property_type": "house",
            "location": "Suburbs",
            "bedrooms": 4,
            "bathrooms": 3,
            "area": 2500,
            "status": "active"
        }
    ]
    
    for property_data in test_properties:
        create_property(property_data)

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    print("\nTest credentials:")
    print("Email: admin@realestate.com")
    print("Password: admin123") 