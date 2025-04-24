# Load environment variables first, before other imports
import os
from pathlib import Path
from dotenv import load_dotenv

# Try to locate and load .env file
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"Main: Loaded environment variables from {env_path}")
else:
    print(f"Main: Warning: .env file not found at {env_path}")

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routers import properties
from .api.v1.endpoints import auth  # Import the auth endpoints
from .core.firebase import initialize_firebase
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Real Estate API",
    description="API for managing real estate properties",
    version="1.0.0",
)

# Initialize Firebase
logger.info("Initializing Firebase...")
firebase_app = initialize_firebase()
if firebase_app == "mock_app":
    logger.warning("Running with mock Firebase implementation")
else:
    logger.info("Firebase initialized successfully")

# Configure CORS
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
logger.info(f"Configuring CORS with allowed origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Get client IP and requested path
    client_host = request.client.host if request.client else "unknown"
    method = request.method
    path = request.url.path
    
    logger.info(f"Request started: {method} {path} from {client_host}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"Request completed: {method} {path} - Status: {response.status_code} - "
            f"Took: {process_time:.4f}s"
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {method} {path} - Error: {str(e)} - "
            f"Took: {process_time:.4f}s"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"}
    )

# Include routers
app.include_router(properties.router, tags=["properties"])
# Add auth router
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])

@app.get("/")
async def root():
    logger.info("Health check endpoint accessed")
    # Print environment variables for debugging (only the names, not values)
    env_vars = [key for key in os.environ.keys() if key.startswith("FIREBASE_")]
    logger.info(f"Available Firebase environment variables: {env_vars}")
    
    return {
        "message": "Real Estate API is running",
        "status": "ok",
        "version": app.version,
        "firebase_mode": "mock" if firebase_app == "mock_app" else "production",
        "env_vars_found": len(env_vars)
    } 