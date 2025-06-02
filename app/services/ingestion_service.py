from fastapi import BackgroundTasks
from typing import Union
from app.models.ingestion import IngestionRequest, IngestionResponse
from app.db.mongodb import get_db
from datetime import datetime
import uuid
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger()

# Ingestion statuses as constants or could be an Enum if you prefer
INGESTION_STATUS_PENDING = "pending"
INGESTION_STATUS_PROCESSING = "processing"
INGESTION_STATUS_COMPLETED = "completed"
INGESTION_STATUS_FAILED = "failed"


async def trigger_ingestion(
    request: IngestionRequest,
    user_id: str,
    background_tasks: BackgroundTasks
) -> IngestionResponse:
    """
    Initiates an ingestion process by creating a record and scheduling the worker.
    """
    db = await anext(get_db())
    ingestion_collection = db[settings.INGESTION_COLLECTION]

    ingestion_id = str(uuid.uuid4())
    ingestion_record = {
        "ingestion_id": ingestion_id,
        "user_id": user_id,
        "document_id": request.document_id,
        "status": INGESTION_STATUS_PENDING,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    await ingestion_collection.insert_one(ingestion_record)
    logger.info(f"Ingestion record created: {ingestion_id}")

    background_tasks.add_task(run_ingestion_worker, ingestion_id)

    return IngestionResponse(
        ingestion_id=ingestion_id,
        status=INGESTION_STATUS_PENDING,
        message="Ingestion started in background."
    )


async def run_ingestion_worker(ingestion_id: str) -> None:
    """
    Worker function that processes the document ingestion asynchronously.
    """
    # Import here to avoid circular imports if any
    from app.ingestion.worker import process_document

    db = await anext(get_db())
    ingestion_collection = db[settings.INGESTION_COLLECTION]

    # Update status to processing
    await ingestion_collection.update_one(
        {"ingestion_id": ingestion_id},
        {"$set": {"status": INGESTION_STATUS_PROCESSING, "updated_at": datetime.utcnow()}}
    )
    logger.info(f"Ingestion {ingestion_id} status updated to processing")

    try:
        await process_document(ingestion_id)
    except Exception as e:
        # Log error and update status to failed with error message
        logger.error(f"Ingestion {ingestion_id} failed: {str(e)}", exc_info=True)
        await ingestion_collection.update_one(
            {"ingestion_id": ingestion_id},
            {
                "$set": {
                    "status": INGESTION_STATUS_FAILED,
                    "error": str(e),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return

    # Update status to completed
    await ingestion_collection.update_one(
        {"ingestion_id": ingestion_id},
        {"$set": {"status": INGESTION_STATUS_COMPLETED, "updated_at": datetime.utcnow()}}
    )
    logger.info(f"Ingestion {ingestion_id} completed successfully")
