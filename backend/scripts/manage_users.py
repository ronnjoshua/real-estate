#!/usr/bin/env python3
"""
User Management Script

This script provides utilities to manage users in the memory database, including:
- Listing all users
- Resetting passwords
- Creating new users
- Changing user roles

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
    
    logger.info("Successfully imported app modules")
except ImportError as e:
    logger.error(f"Error importing app modules: {e}")
    sys.exit(1)

def list_users():
    """List all users in the database."""
    if not users_db:
        print("No users found in the database.")
        return
    
    print("\n=== Users in Database ===")
    print(f"{'Email':<30} {'Full Name':<30} {'Role':<10} {'Active':<10} {'Created At'}")
    print("-" * 90)
    
    for user_id, user in users_db.items():
        created_at = user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        active_status = "Yes" if user.is_active else "No"
        print(f"{user.email:<30} {user.full_name:<30} {user.role:<10} {active_status:<10} {created_at}")

def reset_password(email: str, new_password: str):
    """Reset a user's password."""
    user = get_user_by_email(email)
    if not user:
        print(f"User with email '{email}' not found.")
        return
    
    hashed_password = get_password_hash(new_password)
    update_user(email, {"hashed_password": hashed_password})
    print(f"Password reset successfully for user '{email}'.")

def create_new_user(email: str, full_name: str, password: str, role: str):
    """Create a new user."""
    existing_user = get_user_by_email(email)
    if existing_user:
        print(f"User with email '{email}' already exists.")
        return
    
    try:
        user_role = UserRole(role.upper())
    except ValueError:
        print(f"Invalid role '{role}'. Valid roles are: {', '.join([r.value for r in UserRole])}")
        return
    
    hashed_password = get_password_hash(password)
    user = create_user(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        role=user_role
    )
    print(f"User '{email}' created successfully with role '{user_role.value}'.")

def change_user_role(email: str, new_role: str):
    """Change a user's role."""
    user = get_user_by_email(email)
    if not user:
        print(f"User with email '{email}' not found.")
        return
    
    try:
        user_role = UserRole(new_role.upper())
    except ValueError:
        print(f"Invalid role '{new_role}'. Valid roles are: {', '.join([r.value for r in UserRole])}")
        return
    
    update_user(email, {"role": user_role})
    print(f"Role changed successfully for user '{email}' to '{user_role.value}'.")

def main():
    parser = argparse.ArgumentParser(description="User Management Script")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    subparsers.add_parser("list", help="List all users")
    
    # Reset password command
    reset_parser = subparsers.add_parser("reset-password", help="Reset a user's password")
    reset_parser.add_argument("--email", required=True, help="User email")
    reset_parser.add_argument("--password", required=True, help="New password")
    
    # Create user command
    create_parser = subparsers.add_parser("create", help="Create a new user")
    create_parser.add_argument("--email", required=True, help="User email")
    create_parser.add_argument("--name", required=True, help="User full name")
    create_parser.add_argument("--password", required=True, help="User password")
    create_parser.add_argument("--role", required=True, choices=["admin", "client"], help="User role")
    
    # Change role command
    role_parser = subparsers.add_parser("change-role", help="Change a user's role")
    role_parser.add_argument("--email", required=True, help="User email")
    role_parser.add_argument("--role", required=True, choices=["admin", "client"], help="New role")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "list":
        list_users()
    elif args.command == "reset-password":
        reset_password(args.email, args.password)
    elif args.command == "create":
        create_new_user(args.email, args.name, args.password, args.role)
    elif args.command == "change-role":
        change_user_role(args.email, args.role)

if __name__ == "__main__":
    main()