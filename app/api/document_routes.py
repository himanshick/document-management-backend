from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.document import DocumentCreate, DocumentInDB
from app.services.document_service import (
    create_document,
    get_document,
    get_all_documents,
    update_document,
    delete_document,
)
from app.core.auth import decode_access_token
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        user_id: str = payload.sub  # <-- attribute access instead of .get()
        role: str = payload.role
        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"user_id": user_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/", response_model=DocumentInDB)
async def create(doc: DocumentCreate, user=Depends(get_current_user)):
    return await create_document(doc, user["user_id"])

@router.get("/{doc_id}", response_model=DocumentInDB)
async def read(doc_id: str, user=Depends(get_current_user)):
    doc = await get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/", response_model=List[DocumentInDB])
async def read_all(user=Depends(get_current_user)):
    return await get_all_documents(user["user_id"], user["role"])

@router.put("/{doc_id}", response_model=DocumentInDB)
async def update(doc_id: str, doc: DocumentCreate, user=Depends(get_current_user)):
    updated = await update_document(doc_id, doc, user["user_id"], user["role"])
    if not updated:
        raise HTTPException(status_code=404, detail="Document not found or unauthorized")
    return updated

@router.delete("/{doc_id}")
async def delete(doc_id: str, user=Depends(get_current_user)):
    deleted = await delete_document(doc_id, user["user_id"], user["role"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found or unauthorized")
    return {"message": "Document deleted successfully"}
