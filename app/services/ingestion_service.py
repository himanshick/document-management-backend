# app/services/ingestion_service.py

from fastapi import BackgroundTasks
from app.models.ingestion import IngestionRequest, IngestionResponse
from app.db.mongodb import get_db
from bson.objectid import ObjectId
from datetime import datetime
import uuid


async def trigger_ingestion(
    request: IngestionRequest,
    user_id: str,
    background_tasks: BackgroundTasks
) -> IngestionResponse:
    db = get_db()
    ingestion_collection = db["ingestions"]

    # Create a new ingestion record
    ingestion_id = str(uuid.uuid4())
    ingestion_record = {
        "ingestion_id": ingestion_id,
        "user_id": user_id,
        "document_id": request.document_id,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    await ingestion_collection.insert_one(ingestion_record)

    # Start background ingestion processing
    background_tasks.add_task(run_ingestion_worker, ingestion_id)

    return IngestionResponse(
        ingestion_id=ingestion_id,
        status="pending",
        message="Ingestion started in background."
    )


async def run_ingestion_worker(ingestion_id: str):
    from app.ingestion.worker import process_document

    db = get_db()
    ingestion_collection = db["ingestions"]

    # Update status to "processing"
    await ingestion_collection.update_one(
        {"ingestion_id": ingestion_id},
        {"$set": {"status": "processing", "updated_at": datetime.utcnow()}}
    )

    try:
        # Do the actual ingestion work
        await process_document(ingestion_id)

        # Update status to "completed"
        await ingestion_collection.update_one(
            {"ingestion_id": ingestion_id},
            {"$set": {"status": "completed", "updated_at": datetime.utcnow()}}
        )
    except Exception as e:
        # Update status to "failed" and log the error
        await ingestion_collection.update_one(
            {"ingestion_id": ingestion_id},
            {
                "$set": {
                    "status": "failed",
                    "error": str(e),
                    "updated_at": datetime.utcnow()
                }
            }
        )
