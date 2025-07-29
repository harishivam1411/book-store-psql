from pydantic import BaseModel, Field
from datetime import datetime, timezone

class BaseSchema(BaseModel):
    id: int = Field(..., examples=[1])
    name: str = Field(..., examples=["F. Scott Fitzgerald"])

class BookBaseSchema(BaseModel):
    id: int = Field(..., examples=[1])
    title: str = Field(..., examples=["The Great Gatsby"])

class UserBaseSchema(BaseModel):
    id: int = Field(..., examples=[1])
    username: str = Field(..., examples=["booklover99"])

class CreateSchema(BaseModel):
    id: int = Field(..., examples=[1])
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CreateUpdateSchema(BaseModel):
    id: int = Field(..., examples=[1])
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

