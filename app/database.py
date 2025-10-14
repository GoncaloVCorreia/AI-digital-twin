"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your actual database URL
import os
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://correia:postgres@db:5432/ai_project_db"
)

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True,  connect_args={"options": "-c client_encoding=UTF8"}
)

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
