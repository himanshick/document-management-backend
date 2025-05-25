# app/models/ingestion.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class IngestionRequest(BaseModel):
    document_id: str


class IngestionResponse(BaseModel):
    ingestion_id: str
    status: str
    message: str


class IngestionStatus(BaseModel):
    ingestion_id: str
    document_id: str
    user_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None
