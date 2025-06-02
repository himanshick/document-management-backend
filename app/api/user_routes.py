import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError

from app.models.user import UserCreate, Token, TokenData, UserInDB
from app.services.user_service import register_user, authenticate_user, get_all_users, get_user_by_id
from app.core.auth import decode_access_token

logger = logging.getLogger(__name__)
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    try:
        payload: TokenData = decode_access_token(token)
        if not payload.sub or not payload.role:
            logger.warning("Invalid token payload, missing user ID or role")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


async def require_admin(user: TokenData = Depends(get_current_user)) -> TokenData:
    if user.role != "Admin":
        logger.warning(f"User {user.sub} with role {user.role} attempted admin-only operation")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")
    return user


@router.get("/", response_model=List[UserInDB])
async def list_users(admin_user: TokenData = Depends(require_admin)):
    # Only admins can list users
    return await get_all_users()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserInDB)
async def register(user: UserCreate):
    return await register_user(user)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await authenticate_user(form_data.username, form_data.password)


@router.get("/whoami", response_model=TokenData)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserInDB)
async def get_user(user_id: str, current_user: TokenData = Depends(get_current_user)):
    user = await get_user_by_id(user_id)
    if not user:
        logger.info(f"User with id {user_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
