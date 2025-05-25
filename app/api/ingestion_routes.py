# app/api/ingestion_routes.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.services.ingestion_service import trigger_ingestion
from app.models.ingestion import IngestionRequest, IngestionResponse
from app.core.auth import decode_access_token
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/trigger", response_model=IngestionResponse)
async def trigger_ingestion_pipeline(
    request: IngestionRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
):
    try:
        response = await trigger_ingestion(request, user_id, background_tasks)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
