import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.models.document import DocumentCreate, DocumentInDB
from app.models.user import TokenData
from app.services.document_service import (
    create_document,
    get_document,
    get_all_documents,
    update_document,
    delete_document,
)
from app.core.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=DocumentInDB, status_code=status.HTTP_201_CREATED)
async def create_new_document(
    doc: DocumentCreate,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"User {current_user._id} is creating a new document.")
    try:
        new_doc = await create_document(doc, current_user._id)
        logger.info(f"Document created with ID: {new_doc.id} by user {current_user._id}.")
        return new_doc
    except Exception as e:
        logger.error(f"Error creating document for user {current_user._id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document")


@router.get("/{doc_id}", response_model=DocumentInDB)
async def get_document_by_id(
    doc_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"User {current_user._id} requested document {doc_id}.")
    document = await get_document(doc_id)
    if not document:
        logger.warning(f"Document {doc_id} not found for user {current_user._id}.")
        raise HTTPException(status_code=404, detail="Document not found")
    # Optional: check if user is authorized to view document here (if required)
    return document


@router.get("/", response_model=List[DocumentInDB])
async def list_all_documents(
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"User {current_user._id} requested list of all documents.")
    try:
        documents = await get_all_documents(current_user._id, current_user.role)
        return documents
    except Exception as e:
        logger.error(f"Error fetching documents list for user {current_user._id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")


@router.put("/{doc_id}", response_model=DocumentInDB)
async def update_existing_document(
    doc_id: str,
    doc: DocumentCreate,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"User {current_user._id} attempts to update document {doc_id}.")
    updated_doc = await update_document(doc_id, doc, current_user._id, current_user.role)
    if not updated_doc:
        logger.warning(f"Update failed or unauthorized for document {doc_id} by user {current_user._id}.")
        raise HTTPException(status_code=404, detail="Document not found or unauthorized")
    logger.info(f"Document {doc_id} updated successfully by user {current_user._id}.")
    return updated_doc


@router.delete("/{doc_id}", status_code=status.HTTP_200_OK)
async def delete_existing_document(
    doc_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    logger.info(f"User {current_user._id} attempts to delete document {doc_id}.")
    deleted = await delete_document(doc_id, current_user._id, current_user.role)
    if not deleted:
        logger.warning(f"Delete failed or unauthorized for document {doc_id} by user {current_user._id}.")
        raise HTTPException(status_code=404, detail="Document not found or unauthorized")
    logger.info(f"Document {doc_id} deleted by user {current_user._id}.")
    return {"message": "Document deleted successfully"}
