from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

db = None

async def connect_db():
    global db
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]

async def close_db():
    global db
    db = None

def get_db():
    return db
