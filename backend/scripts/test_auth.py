#!/usr/bin/env python3
"""
Test Authentication Functions

This script tests authentication functions with the mock database, including:
- Creating users
- Logging in (password verification)
- Creating and validating tokens
- Password hashing and verification

Usage:
  python test_auth.py
"""

import os
import sys
from pathlib import Path
import logging
from datetime import datetime, timedelta
import json
import requests

# Add parent directory to path to import app modules
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

try:
    # Import app modules
    from app.core.security import get_password_hash, verify_password
    from app.models.user import UserRole, UserInDB, User
    from app.db.memory_db import users_db, get_user_by_email, create_user, update_user
    from app.core.auth import create_access_token, verify_token
    
    logger.info("Successfully imported app modules")
except ImportError as e:
    logger.error(f"Error importing app modules: {e}")
    sys.exit(1)

def test_password_hashing():
    """Test password hashing and verification."""
    print("\n=== Testing Password Hashing ===")
    
    # Test passwords
    passwords = ["simple123", "C0mpl3x!P@ssw0rd", "Short1"]
    
    for password in passwords:
        print(f"Testing password: {password}")
        
        # Hash the password
        hashed = get_password_hash(password)
        print(f"  Hashed: {hashed[:20]}...")
        
        # Verify the password
        is_valid = verify_password(password, hashed)
        print(f"  Verification: {'✓ Success' if is_valid else '✗ Failed'}")
        
        # Try incorrect password
        wrong_pass = password + "wrong"
        is_invalid = verify_password(wrong_pass, hashed)
        print(f"  Wrong password test: {'✓ Correctly rejected' if not is_invalid else '✗ Incorrectly accepted'}")
        
        print("")

def test_user_creation():
    """Test user creation and retrieval."""
    print("\n=== Testing User Creation ===")
    
    # Create a test user
    test_email = "test_user@example.com"
    test_password = "testpassword123"
    test_name = "Test User"
    
    # Check if user already exists and delete if needed
    existing_user = get_user_by_email(test_email)
    if existing_user:
        print(f"User {test_email} already exists, will be updated")
    
    # Hash the password
    hashed_password = get_password_hash(test_password)
    
    # Create or update the user
    if existing_user:
        user = update_user(
            email=test_email,
            updates={
                "full_name": test_name,
                "hashed_password": hashed_password
            }
        )
        print(f"Updated user: {user.email}")
    else:
        user = create_user(
            email=test_email,
            full_name=test_name,
            hashed_password=hashed_password,
            role=UserRole.CLIENT
        )
        print(f"Created user: {user.email}")
    
    # Retrieve the user
    retrieved_user = get_user_by_email(test_email)
    if retrieved_user:
        print(f"Retrieved user successfully: {retrieved_user.email}")
        print(f"  Name: {retrieved_user.full_name}")
        print(f"  Role: {retrieved_user.role}")
        print(f"  Created At: {retrieved_user.created_at}")
    else:
        print("Failed to retrieve user")

def test_token_creation():
    """Test token creation and verification."""
    print("\n=== Testing Token Creation ===")
    
    # Create a token
    user_data = {"sub": "test@example.com", "role": "client"}
    expires_delta = timedelta(minutes=30)
    
    token = create_access_token(user_data, expires_delta)
    print(f"Created token: {token[:20]}...")
    
    # Verify the token
    payload = verify_token(token)
    if payload:
        print("Token verification successful")
        print(f"  Payload: {payload}")
    else:
        print("Token verification failed")

def test_authentication_api(api_url="http://localhost:8000"):
    """Test authentication API endpoints."""
    print("\n=== Testing Authentication API ===")
    
    # Test if the API is running
    try:
        response = requests.get(f"{api_url}/")
        if response.status_code == 200:
            print(f"API is running: {response.json()}")
        else:
            print(f"API returned status code: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to API at {api_url}")
        return
    
    # Test registration
    test_user = {
        "email": "api_test@example.com",
        "full_name": "API Test User",
        "password": "testpassword123",
        "role": "client"
    }
    
    print("\nTesting registration...")
    try:
        response = requests.post(
            f"{api_url}/api/v1/auth/register",
            json=test_user
        )
        
        if response.status_code == 200:
            print("Registration successful")
            print(f"  Response: {response.json()}")
        elif response.status_code == 400:
            print("User already exists")
            print(f"  Response: {response.json()}")
        else:
            print(f"Registration failed with status code: {response.status_code}")
            print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"Error testing registration: {e}")
    
    # Test login
    print("\nTesting login...")
    try:
        response = requests.post(
            f"{api_url}/api/v1/auth/token",
            data={
                "username": test_user["email"],
                "password": test_user["password"]
            }
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("Login successful")
            print(f"  Access Token: {token_data['access_token'][:20]}...")
            
            # Test user info with token
            print("\nTesting user info retrieval...")
            user_response = requests.get(
                f"{api_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            
            if user_response.status_code == 200:
                print("User info retrieval successful")
                print(f"  User: {user_response.json()}")
            else:
                print(f"User info retrieval failed with status code: {user_response.status_code}")
                print(f"  Response: {user_response.json()}")
        else:
            print(f"Login failed with status code: {response.status_code}")
            print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"Error testing login: {e}")

def main():
    print("Testing authentication functionality with mock database")
    
    test_password_hashing()
    test_user_creation()
    test_token_creation()
    
    # Check if API testing is enabled
    api_test = input("\nDo you want to test the authentication API? (y/n): ").lower()
    if api_test == 'y':
        api_url = input("Enter API URL (default: http://localhost:8000): ") or "http://localhost:8000"
        test_authentication_api(api_url)
    
    print("\nTests completed!")

if __name__ == "__main__":
    main() 