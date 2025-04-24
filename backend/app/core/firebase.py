# Temporarily disable Firebase
# This file will be updated when Firebase is set up
import firebase_admin
from firebase_admin import credentials
from .config import settings
import logging
import os
import json

# Set up logger
logger = logging.getLogger(__name__)

_firebase_app = None

def validate_firebase_credentials():
    """Validate if all required Firebase credentials are present."""
    required_env_vars = [
        "FIREBASE_TYPE",
        "FIREBASE_PROJECT_ID",
        "FIREBASE_PRIVATE_KEY_ID",
        "FIREBASE_PRIVATE_KEY",
        "FIREBASE_CLIENT_EMAIL",
        "FIREBASE_CLIENT_ID",
        "FIREBASE_AUTH_URI",
        "FIREBASE_TOKEN_URI",
        "FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
        "FIREBASE_CLIENT_X509_CERT_URL"
    ]
    
    # Check if environment variables are set
    missing_env_vars = [var for var in required_env_vars if not os.environ.get(var)]
    if missing_env_vars:
        logger.warning(f"Missing environment variables: {', '.join(missing_env_vars)}")
        return False
    
    # All required variables are present
    return True

def get_firebase_credentials():
    """Get Firebase credentials either from environment variables or fallback to mock."""
    # First check if we should use mock Firebase
    use_mock = os.environ.get("USE_MOCK_FIREBASE", "").lower() in ("true", "1", "yes")
    if use_mock:
        logger.info("Using mock Firebase as specified in USE_MOCK_FIREBASE")
        return "mock"
    
    # Then validate that all required credentials are present
    if not validate_firebase_credentials():
        logger.warning("Firebase credentials validation failed, falling back to mock")
        return "mock"
    
    # Create credentials dict directly from environment variables
    creds_dict = {
        "type": os.environ.get("FIREBASE_TYPE"),
        "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
        "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
        "auth_uri": os.environ.get("FIREBASE_AUTH_URI"),
        "token_uri": os.environ.get("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.environ.get("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL"),
    }
    
    return creds_dict

def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized."""
    global _firebase_app
    
    if _firebase_app is None:
        # Get credentials
        creds = get_firebase_credentials()
        
        if creds == "mock":
            logger.warning("Using mock Firebase implementation")
            _firebase_app = "mock_app"
            return _firebase_app
        
        try:
            # Try to initialize Firebase with credentials
            logger.info("Initializing Firebase with credentials from environment variables")
            firebase_cred = credentials.Certificate(creds)
            _firebase_app = firebase_admin.initialize_app(firebase_cred)
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
            logger.warning("Falling back to mock Firebase app")
            _firebase_app = "mock_app"
    
    return _firebase_app

def get_firebase_app():
    """Get the Firebase app instance, initializing if necessary."""
    global _firebase_app
    
    if _firebase_app is None:
        return initialize_firebase()
    
    return _firebase_app

def reset_firebase_app():
    """Reset the Firebase app for testing purposes."""
    global _firebase_app
    
    if _firebase_app and _firebase_app != "mock_app":
        try:
            firebase_admin.delete_app(_firebase_app)
        except Exception as e:
            logger.error(f"Error deleting Firebase app: {e}")
    
    _firebase_app = None
    return _firebase_app is None

def get_db():
    """Get Firestore database client."""
    app = get_firebase_app()
    if app == "mock_app":
        return None
    
    try:
        from firebase_admin import firestore
        return firestore.client(app)
    except Exception as e:
        logger.error(f"Error getting Firestore client: {e}")
        return None

db = get_db() 