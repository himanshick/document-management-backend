from fastapi import HTTPException
from app.models.user import UserCreate, UserInDB, TokenData
from app.db.mongodb import get_db
from app.core.auth import hash_password, verify_password, create_access_token
from bson.objectid import ObjectId
from app.core.logger import get_logger

logger = get_logger()

async def register_user(user: UserCreate):
    try:
        logger.info(f"Trying to register user: {user.email}")
        db = get_db()
        
        user_collection = db["users"]

        existing_user = await user_collection.find_one({"email": user.email})
        logger.info(f"Existing user found: {existing_user}")

        if existing_user is not None:
            raise HTTPException(400, "Email already registered")


        logger.info(f"user obj before insert: {user.dict()}")
        user_dict = user.dict()
        logger.info(f"user obj before insert: {user_dict}")
        user_dict["hashed_password"] = hash_password(user.password)
        del user_dict["password"]
        
        logger.info(f"user obj after hash: {user_dict}")

        result = await user_collection.insert_one(user_dict)
        logger.info(f"User successfully registered with id: {result.inserted_id}")
        return {"id": str(result.inserted_id), "email": user.email, "role": user.role.value}
    except Exception as e:
        logger.error(f"Error in registration: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


async def authenticate_user(email: str, password: str):
    db = get_db()
    user_collection = db["users"]
    user = await user_collection.find_one({"email": email})
    if not user or not verify_password(password, user.get("hashed_password")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token_data = {"sub": str(user["_id"]), "role": user["role"]}
    token = create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer"}


async def get_all_users():
    db = get_db()
    user_collection = db["users"]
    users_cursor = user_collection.find({})
    users = await users_cursor.to_list(length=None)
    
    result = []
    for user in users:
        user['id'] = str(user['_id'])  # convert ObjectId to string
        del user['_id']               # remove original _id to avoid confusion
        result.append(UserInDB(**user))
    return result

async def get_user_by_id(user_id: str) -> UserInDB | None:
    db = get_db()
    user_collection = db["users"]

    # Validate ObjectId
    if not ObjectId.is_valid(user_id):
        return None

    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user['id'] = str(user['_id'])
        del user['_id']
        return UserInDB(**user)
    return None