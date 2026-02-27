from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Handle Neon's connection string format
if DATABASE_URL:
    # Remove channel_binding parameter if present (not supported by psycopg2)
    if "channel_binding" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.split("&channel_binding")[0]
    logger.info("Database URL configured")
else:
    logger.warning("DATABASE_URL not set - database operations will fail")

# Create engine
engine = None
SessionLocal = None

if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        echo=False
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    if SessionLocal is None:
        raise Exception("Database not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    if engine is None:
        logger.error("Cannot initialize database - no engine configured")
        return False

    try:
        # Import models to register them with Base
        from app.db import models  # noqa: F401

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False
