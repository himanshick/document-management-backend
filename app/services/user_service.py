from fastapi import HTTPException, status
from app.models.user import UserCreate, UserInDB, TokenData
from app.db.mongodb import get_db
from app.core.auth import hash_password, verify_password, create_access_token
from bson.objectid import ObjectId
from app.core.logger import get_logger
from typing import List, Optional
from app.core.config import settings

logger = get_logger()

async def register_user(user: UserCreate) -> dict:
    try:
        logger.info(f"Trying to register user: {user.email}")
        db = await anext(get_db())
        user_collection = db[settings.USER_COLLECTION]

        existing_user = await user_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        user_dict = user.dict()
        user_dict["hashed_password"] = hash_password(user.password)
        del user_dict["password"]

        result = await user_collection.insert_one(user_dict)
        logger.info(f"User successfully registered with id: {result.inserted_id}")

        return {"id": str(result.inserted_id), "email": user.email, "role": user.role.value}
    except Exception as e:
        logger.error(f"Error in registration: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def authenticate_user(email: str, password: str) -> dict:
    try:
        db = await anext(get_db())
        user_collection = db[settings.USER_COLLECTION]
        user = await user_collection.find_one({"email": email})
        if not user or not verify_password(password, user.get("hashed_password")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        token_data = {"sub": str(user["_id"]), "role": user["role"]}
        token = create_access_token(token_data)
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise  # re-raise known HTTP exceptions
    except Exception as e:
        logger.error(f"Error during authentication: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


async def get_all_users() -> List[UserInDB]:
    db = await anext(get_db())
    user_collection = db[settings.USER_COLLECTION]
    users_cursor = user_collection.find({})
    users = await users_cursor.to_list(length=10)  # limit to 10 max or implement pagination
    
    result = []
    for user in users:
        user['id'] = str(user['_id'])
        del user['_id']
        result.append(UserInDB(**user))
    return result


async def get_user_by_id(user_id: str) -> Optional[UserInDB]:
    db = await anext(get_db())
    user_collection = db[settings.USER_COLLECTION]

    if not ObjectId.is_valid(user_id):
        return None

    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user['id'] = str(user['_id'])
        del user['_id']
        return UserInDB(**user)
    return None
