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
from .api.v1.endpoints import auth, properties_unified, contact
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


# Configure CORS
from .core.config import get_settings
settings = get_settings()

# Get allowed origins from settings
try:
    origins = settings.get_allowed_origins()
    logger.info(f"Configuring CORS with allowed origins: {origins}")
    
    # Check if we're using wildcard with credentials (not allowed)
    allow_credentials = True
    if "*" in origins:
        logger.warning("Using wildcard origin '*' - disabling credentials for security")
        allow_credentials = False
        
except Exception as e:
    logger.error(f"Error getting allowed origins: {e}")
    # Fallback to allow all origins for now
    origins = ["*"]
    allow_credentials = False
    logger.warning("Using fallback CORS policy: allow all origins, no credentials")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security headers middleware
@app.middleware("http") 
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

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

# Initialize database on startup
from .db.memory_db import initialize_database

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Real Estate API...")
    initialize_database()
    logger.info("Startup complete")

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(properties_unified.router, prefix=f"{settings.API_V1_STR}/properties", tags=["properties"])
app.include_router(contact.router, prefix=f"{settings.API_V1_STR}/contact", tags=["contact"])

@app.get("/")
async def root():
    logger.info("Health check endpoint accessed")
    
    return {
        "message": "Real Estate API is running",
        "status": "ok",
        "version": app.version
    } 