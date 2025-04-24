#!/usr/bin/env python3
"""
Script to test loading of environment variables from .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Find .env file
backend_dir = Path(__file__).parent
env_path = backend_dir / '.env'

print(f"Looking for .env file at: {env_path}")
print(f"File exists: {env_path.exists()}")

if env_path.exists():
    print(f"Loading environment variables from: {env_path}")
    load_dotenv(env_path)
    print("Environment variables loaded")
else:
    print("ERROR: .env file not found!")

# Check Firebase environment variables
firebase_vars = [
    "FIREBASE_TYPE",
    "FIREBASE_PROJECT_ID",
    "FIREBASE_PRIVATE_KEY_ID",
    "FIREBASE_PRIVATE_KEY",
    "FIREBASE_CLIENT_EMAIL",
    "FIREBASE_CLIENT_ID",
    "FIREBASE_AUTH_URI",
    "FIREBASE_TOKEN_URI",
    "FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
    "FIREBASE_CLIENT_X509_CERT_URL",
]

print("\nChecking Firebase environment variables:")
for var in firebase_vars:
    value = os.getenv(var)
    if value:
        # Don't print the full private key
        if var == "FIREBASE_PRIVATE_KEY":
            print(f"{var}: [PRIVATE KEY IS SET]")
        else:
            # Only print first 10 characters for security
            print(f"{var}: {value[:10]}...")
    else:
        print(f"{var}: NOT SET")

if all(os.getenv(var) for var in firebase_vars):
    print("\nAll required Firebase environment variables are set.")
else:
    print("\nWARNING: Some Firebase environment variables are missing!")

# Test creating credentials dict
print("\nTesting credentials dictionary creation:")
creds = {
    "type": os.getenv("FIREBASE_TYPE", ""),
    "project_id": os.getenv("FIREBASE_PROJECT_ID", ""),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL", ""),
    "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI", ""),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI", ""),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", ""),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL", ""),
}

for key in creds:
    if key == "private_key":
        print(f"{key}: {'[SET]' if creds[key] else '[MISSING]'}")
    else:
        print(f"{key}: {'[SET]' if creds[key] else '[MISSING]'}")

print("\nDone testing environment variables.") 