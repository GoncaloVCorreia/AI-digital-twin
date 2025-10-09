from fastapi import FastAPI
import uvicorn
import logging

from app.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.personas import router as personas_router
from app.middleware.logging import RequestLoggingMiddleware, SecurityHeadersMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings  # or wherever your Settings class is


# Set up logging
logger = logging.getLogger("uvicorn.error")

# Create all tables (if not using Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Digital Twin API")

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # You can be specific if needed
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Include routers
app.include_router(auth_router)
app.include_router(personas_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


