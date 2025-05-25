# app/services/document_service.py

from fastapi import HTTPException
from app.models.document import DocumentCreate, DocumentInDB
from app.db.mongodb import get_db
from bson import ObjectId

def document_helper(doc) -> dict:
    return {
        "id": str(doc["_id"]),
        "title": doc["title"],
        "content": doc["content"],
        "owner_id": str(doc["owner_id"]),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }

async def create_document(doc: DocumentCreate, user_id: str):
    db = get_db()
    doc_collection = db["documents"]

    doc_dict = doc.dict()
    doc_dict["owner_id"] = ObjectId(user_id)

    result = await doc_collection.insert_one(doc_dict)
    created_doc = await doc_collection.find_one({"_id": result.inserted_id})
    return document_helper(created_doc)

async def get_document(doc_id: str):
    db = get_db()
    doc_collection = db["documents"]

    try:
        obj_id = ObjectId(doc_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document ID")

    doc = await doc_collection.find_one({"_id": obj_id})
    if doc:
        return document_helper(doc)
    return None

async def get_all_documents(user_id: str, role: str):
    db = get_db()
    doc_collection = db["documents"]

    if role == "Admin":
        cursor = doc_collection.find({})
    else:
        cursor = doc_collection.find({"owner_id": ObjectId(user_id)})

    docs = await cursor.to_list(length=100)
    return [document_helper(doc) for doc in docs]

async def update_document(doc_id: str, updated_doc: DocumentCreate, user_id: str, role: str):
    db = get_db()
    doc_collection = db["documents"]

    try:
        obj_id = ObjectId(doc_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document ID")

    existing = await doc_collection.find_one({"_id": obj_id})
    if not existing:
        return None

    if role != "Admin" and str(existing["owner_id"]) != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    updated_data = updated_doc.dict()
    await doc_collection.update_one({"_id": obj_id}, {"$set": updated_data})

    new_doc = await doc_collection.find_one({"_id": obj_id})
    return document_helper(new_doc)

async def delete_document(doc_id: str, user_id: str, role: str):
    db = get_db()
    doc_collection = db["documents"]

    try:
        obj_id = ObjectId(doc_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document ID")

    existing = await doc_collection.find_one({"_id": obj_id})
    if not existing:
        return None

    if role != "Admin" and str(existing["owner_id"]) != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    await doc_collection.delete_one({"_id": obj_id})
    return True
