import asyncio
import logging
from datetime import datetime
from typing import Optional
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

logger = logging.getLogger(__name__)

class IngestionWorker:
    def __init__(
        self,
        ingestion_collection: AsyncIOMotorCollection,
        document_collection: AsyncIOMotorCollection,
        max_retries: int = 3,
        retry_delay_seconds: int = 2,
    ):
        self.ingestion_collection = ingestion_collection
        self.document_collection = document_collection
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

    async def _update_ingestion_status(
        self,
        ingestion_id: ObjectId,
        status: str,
        error: Optional[str] = None
    ):
        update_doc = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        if error:
            update_doc["error"] = error

        await self.ingestion_collection.update_one(
            {"_id": ingestion_id},
            {"$set": update_doc}
        )

    async def process_document(self, document_id: str, user_id: str):
        """
        Process the ingestion for a given document and user.

        Inserts a new ingestion record, simulates processing,
        updates document status and ingestion status accordingly.
        """
        ingestion_record = {
            "document_id": document_id,
            "user_id": user_id,
            "status": "processing",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "error": None,
        }

        result = await self.ingestion_collection.insert_one(ingestion_record)
        ingestion_id = result.inserted_id

        for attempt in range(1, self.max_retries + 1):
            try:
                # Simulate a long-running ingestion process
                await asyncio.sleep(2)

                # Update the document status after ingestion (example: mark as indexed)
                update_result = await self.document_collection.update_one(
                    {"_id": ObjectId(document_id)},
                    {"$set": {"indexed": True}}
                )
                if update_result.matched_count == 0:
                    raise ValueError(f"Document with id {document_id} not found")

                await self._update_ingestion_status(ingestion_id, "completed")
                logger.info(f"Ingestion completed for document {document_id}")
                return

            except Exception as e:
                logger.error(f"Error processing ingestion for document {document_id}, attempt {attempt}: {e}")
                if attempt == self.max_retries:
                    await self._update_ingestion_status(ingestion_id, "failed", error=str(e))
                    logger.error(f"Ingestion failed permanently for document {document_id}")
                else:
                    await asyncio.sleep(self.retry_delay_seconds * attempt)
