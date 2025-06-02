from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class IngestionRequest(BaseModel):
    """
    Schema for requesting ingestion processing of a document.
    """
    document_id: str = Field(..., example="60d21b4667d0d8992e610c85", description="ID of the document to ingest")


class IngestionResponse(BaseModel):
    """
    Response after triggering ingestion process.
    """
    ingestion_id: str = Field(..., example="610b0f4e1234567890abcdef", description="Unique ingestion job identifier")
    status: str = Field(..., example="processing", description="Current ingestion status")
    message: Optional[str] = Field(None, example="Ingestion started", description="Optional informational message")


class IngestionStatus(BaseModel):
    """
    Detailed ingestion status report.
    """
    ingestion_id: str = Field(..., example="610b0f4e1234567890abcdef")
    document_id: str = Field(..., example="60d21b4667d0d8992e610c85")
    user_id: str = Field(..., example="user123")
    status: str = Field(..., example="completed")
    created_at: datetime = Field(..., example="2023-01-01T12:00:00Z")
    updated_at: datetime = Field(..., example="2023-01-01T12:30:00Z")
    error: Optional[str] = Field(None, example="Timeout error", description="Error message if ingestion failed")

    class Config:
        orm_mode = True
