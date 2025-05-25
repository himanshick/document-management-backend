# app/ingestion/worker.py

from datetime import datetime
from app.db.mongodb import get_db
from bson.objectid import ObjectId
import asyncio

async def process_document(document_id: str, user_id: str):
    db = get_db()
    ingestion_collection = db["ingestions"]
    document_collection = db["documents"]

    ingestion_record = {
        "document_id": document_id,
        "user_id": user_id,
        "status": "processing",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "error": None
    }

    result = await ingestion_collection.insert_one(ingestion_record)
    ingestion_id = result.inserted_id

    try:
        # Simulate a long-running ingestion process
        await asyncio.sleep(2)

        # Update the document status after ingestion (example: mark as indexed)
        await document_collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"indexed": True}}
        )

        await ingestion_collection.update_one(
            {"_id": ingestion_id},
            {"$set": {
                "status": "completed",
                "updated_at": datetime.utcnow()
            }}
        )
    except Exception as e:
        await ingestion_collection.update_one(
            {"_id": ingestion_id},
            {"$set": {
                "status": "failed",
                "error": str(e),
                "updated_at": datetime.utcnow()
            }}
        )
