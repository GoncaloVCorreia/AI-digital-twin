"""
Persona Pydantic schemas.
"""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool


# ---------- Persona Schemas ----------

MAX_LEN = 512


class PersonaBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=MAX_LEN)
    age: int = Field(..., ge=0, le=120)
    location: str = Field(..., min_length=1, max_length=MAX_LEN)
    description: str = Field(..., min_length=1, max_length=MAX_LEN)
    education: str = Field(..., min_length=1, max_length=MAX_LEN)
    tech_skills: str = Field(..., min_length=1, max_length=MAX_LEN)
    soft_skills: str = Field(..., min_length=1, max_length=MAX_LEN)
    strenghts: str = Field(..., min_length=1, max_length=MAX_LEN)
    weaknesses: str = Field(..., min_length=1, max_length=MAX_LEN)
    goals: str = Field(..., min_length=1, max_length=MAX_LEN)
    hobbies: str = Field(..., min_length=1, max_length=MAX_LEN)
    personality: str = Field(..., min_length=1, max_length=MAX_LEN)
    data_path: Optional[str] = Field("",  max_length=MAX_LEN)
    avatar: Optional[str] = Field("default", max_length=256)  # Add this line

    @field_validator(
        "name",
        "location",
        "description",
        "education",
        "tech_skills",
        "soft_skills",
        "strenghts",
        "weaknesses",
        "goals",
        "hobbies",
        "personality",
        mode="before",
    )
    @classmethod
    def strip_strings(cls, v: str) -> str:
        if isinstance(v, str):
            vs = v.strip()
            if not vs:
                raise ValueError("Field must be a non-empty string")
            return vs
        return v
    @field_validator("data_path", mode="before")
    @classmethod
    def normalize_data_path(cls, v: Union[str, None]) -> str:
        # Allow None -> "", allow empty after strip
        if v is None:
            return ""
        if isinstance(v, str):
            return v.strip()
        return v
    @field_validator("avatar", mode="before")
    @classmethod
    def normalize_avatar(cls, v: Union[str, None]) -> str:
        if v is None:
            return "default"
        if isinstance(v, str):
            return v.strip() or "default"
        return "default"


class PersonaCreate(PersonaBase):
    """Payload for creating a persona."""
    pass


class PersonaUpdate(BaseModel):
    """Partial update; all fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    age: Optional[int] = Field(None, ge=0, le=120)
    location: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    description: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    education: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    tech_skills: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    soft_skills: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    strenghts: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    weaknesses: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    goals: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    hobbies: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    personality: Optional[str] = Field(None, min_length=1, max_length=MAX_LEN)
    data_path: Optional[str] = Field(None, max_length=MAX_LEN)
    avatar: Optional[str] = Field(None, max_length=256)  # Add this line


class Persona(PersonaBase):
    """Response model."""
    id: int

    class Config:
        from_attributes = True
