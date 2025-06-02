from fastapi import HTTPException, status
from typing import List, Optional, Union
from bson import ObjectId, errors
from app.models.document import DocumentCreate, DocumentInDB
from app.db.mongodb import get_db
from app.models.user import UserRole
from app.core.config import settings

MAX_DOCS_RETURN = 100

def document_helper(doc: dict) -> dict:
    """
    Converts MongoDB document to dictionary with string IDs.
    """
    return {
        "id": str(doc["_id"]),
        "title": doc["title"],
        "content": doc["content"],
        "owner_id": str(doc["owner_id"]),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }

async def create_document(doc: DocumentCreate, user_id: str) -> dict:
    db = await get_db()
    doc_collection = db[settings.DOCUMENT_COLLECTION]

    doc_dict = doc.dict()
    try:
        doc_dict["owner_id"] = ObjectId(user_id)
    except errors.InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

    result = await doc_collection.insert_one(doc_dict)
    created_doc = await doc_collection.find_one({"_id": result.inserted_id})
    return document_helper(created_doc)

async def get_document(doc_id: str) -> Optional[dict]:
    db = await get_db()
    doc_collection = db[settings.DOCUMENT_COLLECTION]

    try:
        obj_id = ObjectId(doc_id)
    except errors.InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID")

    doc = await doc_collection.find_one({"_id": obj_id})
    if doc:
        return document_helper(doc)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

async def get_all_documents(user_id: str, role: Union[UserRole, str]) -> List[dict]:
    db = await get_db()
    doc_collection = db[settings.DOCUMENT_COLLECTION]

    # Normalize role if string
    role = UserRole(role) if isinstance(role, str) else role

    if role == UserRole.admin:
        cursor = doc_collection.find({})
    else:
        try:
            owner_obj_id = ObjectId(user_id)
        except errors.InvalidId:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
        cursor = doc_collection.find({"owner_id": owner_obj_id})

    docs = await cursor.to_list(length=MAX_DOCS_RETURN)
    return [document_helper(doc) for doc in docs]

async def update_document(
    doc_id: str,
    updated_doc: DocumentCreate,
    user_id: str,
    role: Union[UserRole, str]
) -> dict:
    db = await get_db()
    doc_collection = db[settings.DOCUMENT_COLLECTION]

    try:
        obj_id = ObjectId(doc_id)
    except errors.InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID")

    existing = await doc_collection.find_one({"_id": obj_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    role = UserRole(role) if isinstance(role, str) else role

    if role != UserRole.admin and str(existing["owner_id"]) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    updated_data = updated_doc.dict()
    await doc_collection.update_one({"_id": obj_id}, {"$set": updated_data})

    new_doc = await doc_collection.find_one({"_id": obj_id})
    return document_helper(new_doc)

async def delete_document(doc_id: str, user_id: str, role: Union[UserRole, str]) -> bool:
    db = await get_db()
    doc_collection = db[settings.DOCUMENT_COLLECTION]

    try:
        obj_id = ObjectId(doc_id)
    except errors.InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID")

    existing = await doc_collection.find_one({"_id": obj_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    role = UserRole(role) if isinstance(role, str) else role

    if role != UserRole.admin and str(existing["owner_id"]) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    await doc_collection.delete_one({"_id": obj_id})
    return True
