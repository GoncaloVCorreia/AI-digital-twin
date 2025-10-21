"""
Minimal Persona model.

CREATE TABLE personas (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(512) NOT NULL,
    age         INTEGER NOT NULL,
    location    VARCHAR(512) NOT NULL,
    description VARCHAR(512) NOT NULL,
    education   VARCHAR(512) NOT NULL,
    tech_skills VARCHAR(512) NOT NULL,
    soft_skills VARCHAR(512) NOT NULL,
    strenghts   VARCHAR(512) NOT NULL,
    weaknesses  VARCHAR(512) NOT NULL,
    goals       VARCHAR(512) NOT NULL,
    hobbies     VARCHAR(512) NOT NULL,
    personality VARCHAR(512) NOT NULL,
    avatar      VARCHAR(256) NOT NULL
)
"""

from __future__ import annotations
from typing import Any, Dict

from sqlalchemy import Column, BigInteger, Integer, String, DateTime
from sqlalchemy.orm import validates
from sqlalchemy.sql import func

# adjust this import path if your database module lives elsewhere
from app.database import Base, engine


class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer().with_variant(BigInteger, "postgresql"), primary_key=True, autoincrement=True)
    name = Column(String(512), nullable=False, index=True , unique=True)
    age = Column(Integer, nullable=False)
    location = Column(String(512), nullable=False)
    description = Column(String(512), nullable=False)
    education = Column(String(512), nullable=False)
    tech_skills = Column(String(512), nullable=False)
    soft_skills = Column(String(512), nullable=False)
    strenghts = Column(String(512), nullable=False)
    weaknesses = Column(String(512), nullable=False)
    goals = Column(String(512), nullable=False)
    hobbies = Column(String(512), nullable=False)
    personality = Column(String(512), nullable=False)
    avatar = Column(String(256), nullable=True, server_default="default")
    data_path = Column(String(1024), nullable=True, server_default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())



