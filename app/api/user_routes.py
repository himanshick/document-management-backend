# app/api/user_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError
from app.models.user import UserCreate, Token, TokenData, UserInDB
from app.services.user_service import register_user, authenticate_user, get_all_users, get_user_by_id
from app.core.auth import decode_access_token
from typing import List

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

@router.get("/", response_model=List[UserInDB])
async def list_users(token: str = Depends(oauth2_scheme)):
    try:
        payload: TokenData = decode_access_token(token)
        # if payload.role != "Admin":
        #     raise HTTPException(status_code=403, detail="Access forbidden")

        return await get_all_users()
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/register", status_code=201)
async def register(user: UserCreate):
    return await register_user(user)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await authenticate_user(form_data.username, form_data.password)


@router.get("/whoami", response_model=TokenData)
async def get_current_user_info(token: str = Depends(oauth2_scheme)):
    try:
        payload: TokenData = decode_access_token(token)

        user_id: str = payload.sub
        role: str = payload.role

        if user_id is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        return TokenData(sub=user_id, role=role)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload format"
        )



@router.get("/{user_id}", response_model=UserInDB)
async def get_user(user_id: str):
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user