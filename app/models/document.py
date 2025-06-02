from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    title: str = Field(..., example="HR Policy", description="Title of the document")
    content: str = Field(..., example="This document contains HR guidelines...", description="Main content of the document")

class DocumentCreate(DocumentBase):
    """Schema used when creating a new document"""
    pass

class DocumentUpdate(BaseModel):
    """Schema used for updating a document - partial fields allowed"""
    title: Optional[str] = Field(None, example="Updated HR Policy")
    content: Optional[str] = Field(None, example="Updated document content...")

class DocumentInDB(DocumentBase):
    id: str = Field(..., alias="_id", description="Document unique identifier")
    owner_id: str = Field(..., description="ID of the user who owns the document")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True  # allows using `id` instead of `_id`
        schema_extra = {
            "example": {
                "id": "60d21b4667d0d8992e610c85",
                "owner_id": "user123",
                "title": "HR Policy",
                "content": "This document contains HR guidelines...",
                "created_at": "2023-01-01T12:00:00Z",
                "updated_at": "2023-01-02T12:00:00Z"
            }
        }

class DocumentResponse(DocumentInDB):
    """Response schema returned by API endpoints"""
    pass
