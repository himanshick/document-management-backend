# app/models/document.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    title: str = Field(..., example="HR Policy")
    content: str = Field(..., example="This document contains HR guidelines...")

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(DocumentBase):
    pass

class DocumentInDB(DocumentBase):
    id: str
    owner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class DocumentResponse(DocumentInDB):
    pass
