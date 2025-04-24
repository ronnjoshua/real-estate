#!/usr/bin/env python3
"""
Script to check if the .env file is properly configured with all required
Firebase credentials.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Required Firebase environment variables
REQUIRED_FIREBASE_VARS = [
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

# Optional environment variables (not required but checked if present)
OPTIONAL_ENV_VARS = [
    "ALLOWED_ORIGINS",
    "USE_MOCK_FIREBASE",
]

def check_env_file(env_path=None):
    """
    Check if the .env file exists and contains all required variables.
    
    Args:
        env_path: Path to the .env file. If None, tries to find it in the current directory
                 or parent directories.
    
    Returns:
        bool: True if all required variables are present, False otherwise.
    """
    # Find .env file if not specified
    if env_path is None:
        env_path = find_env_file()
        if env_path is None:
            logger.error("No .env file found in current directory or parent directories")
            return False
    
    # Check if .env file exists
    env_path = Path(env_path)
    if not env_path.exists():
        logger.error(f".env file not found at {env_path}")
        return False
    
    logger.info(f"Checking .env file at: {env_path}")
    
    # Load .env file
    load_dotenv(env_path)
    
    # Check required variables
    missing_vars = []
    empty_vars = []
    
    for var in REQUIRED_FIREBASE_VARS:
        value = os.getenv(var)
        if value is None:
            missing_vars.append(var)
        elif not value.strip():
            empty_vars.append(var)
    
    # Check optional variables
    optional_present = []
    for var in OPTIONAL_ENV_VARS:
        if os.getenv(var) is not None:
            optional_present.append(var)
    
    # Report results
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    if empty_vars:
        logger.warning(f"Empty values for environment variables: {', '.join(empty_vars)}")
    
    if optional_present:
        logger.info(f"Optional environment variables found: {', '.join(optional_present)}")
    
    if not missing_vars and not empty_vars:
        logger.info("All required environment variables are present")
        return True
    
    return False

def find_env_file():
    """
    Search for .env file in current directory and parent directories.
    
    Returns:
        Path: Path to the .env file, or None if not found.
    """
    current_dir = Path.cwd()
    
    # Look in current directory and up to 3 levels of parent directories
    for _ in range(4):
        env_path = current_dir / ".env"
        if env_path.exists():
            return env_path
        
        # Move to parent directory
        parent_dir = current_dir.parent
        if parent_dir == current_dir:  # Reached root directory
            break
        current_dir = parent_dir
    
    return None

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        env_path = sys.argv[1]
    else:
        env_path = None
    
    if check_env_file(env_path):
        logger.info("Environment check passed successfully")
        return 0
    else:
        logger.error("Environment check failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 