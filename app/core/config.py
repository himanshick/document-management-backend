# app/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    LOG_FILE: str = "app.log"
    USER_COLLECTION: str = "users"
    DOCUMENT_COLLECTION: str = "documents"
    INGESTION_COLLECTION: str = "ingestion"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
