import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the database URL from the environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://correia:postgres@db:5432/ai_project_db"
)


if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not found in environment variables")

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


