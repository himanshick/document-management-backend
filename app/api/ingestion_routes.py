import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.services.ingestion_service import trigger_ingestion
from app.models.ingestion import IngestionRequest, IngestionResponse
from app.core.auth import decode_access_token

logger = logging.getLogger(__name__)
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token payload missing 'sub' claim.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return user_id
    except JWTError as e:
        logger.warning(f"JWT error during token decode: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


@router.post("/trigger", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_ingestion_pipeline(
    request: IngestionRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
):
    logger.info(f"User {user_id} requested ingestion trigger.")
    try:
        response = await trigger_ingestion(request, user_id, background_tasks)
        logger.info(f"Ingestion triggered successfully for user {user_id}.")
        return response
    except Exception as e:
        logger.error(f"Failed to trigger ingestion for user {user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to trigger ingestion")
