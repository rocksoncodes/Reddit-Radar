from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from settings import settings

# ==============================================================================
# Database Configuration
# ==============================================================================

DATABASE_URL = settings.DATABASE_URL

database_engine = create_engine(DATABASE_URL, echo=False, future=True)

SessionLocal = sessionmaker(bind=database_engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_session():
    """
    Utility function to get a new database session.
    """
    return SessionLocal()



# Imported models at the end to avoid circular dependencies
from database import models

__all__ = ["database_engine", "SessionLocal", "Base", "get_session", "models"]
