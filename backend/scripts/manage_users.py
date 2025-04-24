#!/usr/bin/env python3
"""
User Management Script

This script provides utilities to manage users in the system, including:
- Listing all users
- Resetting passwords
- Creating new users
- Changing user roles

It works with both mock database and Firestore database.

Usage:
  python manage_users.py [command] [options]

Commands:
  list                 List all users
  reset-password       Reset a user's password
  create               Create a new user
  change-role          Change a user's role

Examples:
  python manage_users.py list
  python manage_users.py reset-password --email admin@realestate.com --password newpassword
  python manage_users.py create --email new@example.com --name "New User" --password pass123 --role client
  python manage_users.py change-role --email user@example.com --role admin
"""

import os
import sys
import argparse
from pathlib import Path
import logging
from datetime import datetime
import uuid

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
    from app.core.firebase import get_firebase_app, get_db
    
    logger.info("Successfully imported app modules")
except ImportError as e:
    logger.error(f"Error importing app modules: {e}")
    sys.exit(1)

def is_using_mock_db():
    """Check if we're using the mock database."""
    firebase_app = get_firebase_app()
    return firebase_app == "mock_app"

def list_users():
    """List all users in the database."""
    if is_using_mock_db():
        if not users_db:
            print("No users found in the database.")
            return
        
        print("\n=== Users in Database (MOCK) ===")
        print(f"{'Email':<30} {'Full Name':<30} {'Role':<10} {'Created At'}")
        print("-" * 80)
        
        for user_id, user in users_db.items():
            created_at = user.created_at.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{user.email:<30} {user.full_name:<30} {user.role:<10} {created_at}")
    else:
        # Use Firestore
        firestore_db = get_db()
        if not firestore_db:
            print("Firestore database is not available.")
            return
        
        print("\n=== Users in Database (FIRESTORE) ===")
        print(f"{'Email':<30} {'Full Name':<30} {'Role':<10} {'Created At'}")
        print("-" * 80)
        
        users_collection = firestore_db.collection('users')
        users = users_collection.get()
        
        if not users:
            print("No users found in the Firestore database.")
            return
        
        for user_doc in users:
            user_data = user_doc.to_dict()
            email = user_data.get('email', 'N/A')
            full_name = user_data.get('full_name', 'N/A')
            role = user_data.get('role', 'N/A')
            created_at = user_data.get('created_at', datetime.now())
            
            if isinstance(created_at, datetime):
                created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
            else:
                created_at_str = str(created_at)
            
            print(f"{email:<30} {full_name:<30} {role:<10} {created_at_str}")

def reset_password(email, new_password):
    """Reset a user's password."""
    if is_using_mock_db():
        user = get_user_by_email(email)
        if not user:
            print(f"User with email {email} not found.")
            return False
        
        # Hash the new password
        hashed_password = get_password_hash(new_password)
        
        # Update the user
        updated_user = update_user(
            email=email,
            updates={"hashed_password": hashed_password}
        )
        
        if updated_user:
            print(f"Password for user {email} has been reset successfully.")
            return True
        else:
            print(f"Failed to reset password for user {email}.")
            return False
    else:
        # Use Firestore
        firestore_db = get_db()
        if not firestore_db:
            print("Firestore database is not available.")
            return False
        
        # Find the user by email
        users_collection = firestore_db.collection('users')
        query = users_collection.where('email', '==', email).limit(1)
        user_docs = query.get()
        
        user_doc = next(iter(user_docs), None)
        if not user_doc:
            print(f"User with email {email} not found in Firestore.")
            return False
        
        # Hash the new password
        hashed_password = get_password_hash(new_password)
        
        # Update the user document
        user_doc.reference.update({
            'hashed_password': hashed_password,
            'updated_at': datetime.now()
        })
        
        print(f"Password for user {email} has been reset successfully in Firestore.")
        return True

def create_new_user(email, full_name, password, role):
    """Create a new user."""
    if is_using_mock_db():
        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            print(f"User with email {email} already exists.")
            return False
        
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Validate role
        try:
            user_role = UserRole(role.lower())
        except ValueError:
            print(f"Invalid role: {role}. Valid roles are: {[r.value for r in UserRole]}")
            return False
        
        # Create the user
        user = create_user(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=user_role
        )
        
        if user:
            print(f"User {email} has been created successfully with role {user_role}.")
            return True
        else:
            print(f"Failed to create user {email}.")
            return False
    else:
        # Use Firestore
        firestore_db = get_db()
        if not firestore_db:
            print("Firestore database is not available.")
            return False
        
        # Check if user already exists
        users_collection = firestore_db.collection('users')
        query = users_collection.where('email', '==', email).limit(1)
        existing_user = next(iter(query.get()), None)
        
        if existing_user:
            print(f"User with email {email} already exists in Firestore.")
            return False
        
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Validate role
        try:
            user_role = UserRole(role.lower())
        except ValueError:
            print(f"Invalid role: {role}. Valid roles are: {[r.value for r in UserRole]}")
            return False
        
        # Create user document
        now = datetime.now()
        user_data = {
            'id': str(uuid.uuid4()),
            'email': email,
            'full_name': full_name,
            'hashed_password': hashed_password,
            'role': user_role.value,
            'is_active': True,
            'created_at': now,
            'updated_at': now
        }
        
        # Add to Firestore
        users_collection.add(user_data)
        
        print(f"User {email} has been created successfully in Firestore with role {user_role}.")
        return True

def change_user_role(email, role):
    """Change a user's role."""
    if is_using_mock_db():
        user = get_user_by_email(email)
        if not user:
            print(f"User with email {email} not found.")
            return False
        
        # Validate role
        try:
            user_role = UserRole(role.lower())
        except ValueError:
            print(f"Invalid role: {role}. Valid roles are: {[r.value for r in UserRole]}")
            return False
        
        # Update the user
        updated_user = update_user(
            email=email,
            updates={"role": user_role}
        )
        
        if updated_user:
            print(f"Role for user {email} has been changed to {user_role} successfully.")
            return True
        else:
            print(f"Failed to change role for user {email}.")
            return False
    else:
        # Use Firestore
        firestore_db = get_db()
        if not firestore_db:
            print("Firestore database is not available.")
            return False
        
        # Find the user by email
        users_collection = firestore_db.collection('users')
        query = users_collection.where('email', '==', email).limit(1)
        user_docs = query.get()
        
        user_doc = next(iter(user_docs), None)
        if not user_doc:
            print(f"User with email {email} not found in Firestore.")
            return False
        
        # Validate role
        try:
            user_role = UserRole(role.lower())
        except ValueError:
            print(f"Invalid role: {role}. Valid roles are: {[r.value for r in UserRole]}")
            return False
        
        # Update the user document
        user_doc.reference.update({
            'role': user_role.value,
            'updated_at': datetime.now()
        })
        
        print(f"Role for user {email} has been changed to {user_role} successfully in Firestore.")
        return True

def main():
    parser = argparse.ArgumentParser(description="User Management Script")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List users command
    list_parser = subparsers.add_parser("list", help="List all users")
    
    # Reset password command
    reset_parser = subparsers.add_parser("reset-password", help="Reset a user's password")
    reset_parser.add_argument("--email", required=True, help="User's email")
    reset_parser.add_argument("--password", required=True, help="New password")
    
    # Create user command
    create_parser = subparsers.add_parser("create", help="Create a new user")
    create_parser.add_argument("--email", required=True, help="User's email")
    create_parser.add_argument("--name", required=True, help="User's full name")
    create_parser.add_argument("--password", required=True, help="User's password")
    create_parser.add_argument("--role", choices=["admin", "client"], default="client", help="User's role")
    
    # Change role command
    role_parser = subparsers.add_parser("change-role", help="Change a user's role")
    role_parser.add_argument("--email", required=True, help="User's email")
    role_parser.add_argument("--role", choices=["admin", "client"], required=True, help="New role")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_users()
    elif args.command == "reset-password":
        reset_password(args.email, args.password)
    elif args.command == "create":
        create_new_user(args.email, args.name, args.password, args.role)
    elif args.command == "change-role":
        change_user_role(args.email, args.role)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 