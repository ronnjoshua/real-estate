#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.db.memory_db import create_property

# Sample properties
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

def add_sample_data():
    print("Adding sample properties to the database...")
    for i, prop in enumerate(sample_properties):
        try:
            created = create_property(prop)
            print(f"✅ Created property {i+1}: {created['title']} (ID: {created['id']})")
        except Exception as e:
            print(f"❌ Failed to create property {i+1}: {e}")
    
    print("Sample data added successfully!")

if __name__ == "__main__":
    add_sample_data()