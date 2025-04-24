#!/usr/bin/env python3
"""
Script to run the FastAPI application with improved error handling and
configurable options.

Example usage:
    python run.py --host 0.0.0.0 --port 8000 --reload
"""

import os
import sys
import argparse
import logging
import uvicorn
import time
from pathlib import Path
from app.core.config import read_env_file

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("backend.run")

def find_backend_root():
    """Find the root directory of the backend by looking for the app directory."""
    current_dir = Path(__file__).resolve().parent
    return current_dir

def load_environment(env_file=None):
    """Load environment variables from .env file using our custom reader."""
    if env_file is None:
        backend_root = find_backend_root()
        env_file = backend_root / ".env"
    
    if Path(env_file).exists():
        logger.info(f"Loading environment from: {env_file}")
        read_env_file(env_file)
        
        # Check if essential environment variables are loaded
        firebase_vars = [
            "FIREBASE_TYPE",
            "FIREBASE_PROJECT_ID"
        ]
        missing = [var for var in firebase_vars if not os.environ.get(var)]
        if missing:
            logger.warning(f"Missing essential Firebase variables: {', '.join(missing)}")
        else:
            logger.info("Essential Firebase environment variables are loaded")
        
        return True
    else:
        logger.warning(f".env file not found at {env_file}")
        return False

def run_server(host="127.0.0.1", port=8000, reload=False, log_level="info"):
    """Run the FastAPI application with Uvicorn."""
    logger.info(f"Starting server on {host}:{port} (reload={reload})")
    
    try:
        # Try importing the app to catch any import errors before uvicorn tries
        try:
            from app.main import app
            logger.info("Application imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import application: {e}")
            return 1
        
        # Record start time
        start_time = time.time()
        
        # Start the server
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
        )
        
        logger.info(f"Server stopped after running for {time.time() - start_time:.2f} seconds")
        return 0
    
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        return 1

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the FastAPI application")
    
    parser.add_argument(
        "--host", 
        default=os.environ.get("API_HOST", "127.0.0.1"),
        help="Host to bind the server to (default: 127.0.0.1 or API_HOST env var)"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.environ.get("API_PORT", "8000")),
        help="Port to bind the server to (default: 8000 or API_PORT env var)"
    )
    
    parser.add_argument(
        "--reload", 
        action="store_true", 
        default=os.environ.get("API_RELOAD", "").lower() in ("true", "1", "yes"),
        help="Enable auto-reload on code changes (default: False or API_RELOAD env var)"
    )
    
    parser.add_argument(
        "--log-level", 
        default=os.environ.get("API_LOG_LEVEL", "info"),
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level (default: info or API_LOG_LEVEL env var)"
    )
    
    parser.add_argument(
        "--env-file", 
        default=os.environ.get("ENV_FILE"),
        help="Path to .env file (default: .env in current or parent directory)"
    )
    
    parser.add_argument(
        "--skip-env-check", 
        action="store_true",
        help="Skip environment variable validation"
    )

    parser.add_argument(
        "--debug-env", 
        action="store_true",
        help="Print environment variables for debugging (keys only, not values)"
    )
    
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Load environment variables
    load_environment(args.env_file)
    
    # Debug environment variables if requested
    if args.debug_env:
        logger.info("Environment variables debug:")
        for key in sorted(os.environ.keys()):
            if key.startswith("FIREBASE_"):
                if key == "FIREBASE_PRIVATE_KEY":
                    logger.info(f"  {key}: [PRIVATE KEY PRESENT]")
                else:
                    value = os.environ.get(key, "")
                    logger.info(f"  {key}: {value[:10]}..." if value else f"  {key}: empty")
    
    # Run the server
    use_mock = os.environ.get("USE_MOCK_FIREBASE", "").lower() in ("true", "1", "yes")
    if use_mock:
        logger.info("Running with mock Firebase implementation (USE_MOCK_FIREBASE=true)")
    
    return run_server(
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )

if __name__ == "__main__":
    sys.exit(main()) 