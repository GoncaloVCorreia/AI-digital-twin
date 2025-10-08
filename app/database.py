"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your actual database URL
DATABASE_URL = "postgresql://correia:postgres@localhost/ai_project_db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for models to inherit from
Base = declarative_base()

def get_db():
    """
    Dependency that provides a DB session.
    Used in FastAPI or similar frameworks with dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
