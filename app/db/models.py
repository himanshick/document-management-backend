from typing import Any
from pymongo import MongoClient, collection
from bson import ObjectId, errors as bson_errors
from pydantic import BaseModel, validator, Field

# Constants for collection names
USER_COLLECTION_NAME = "users"


class PyObjectId(ObjectId):
    """
    Custom ObjectId type for Pydantic validation.
    Ensures valid ObjectId is used when parsing data.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        try:
            return ObjectId(v)
        except bson_errors.InvalidId as e:
            raise ValueError(f"Invalid ObjectId format: {e}")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserModel(BaseModel):
    """
    Example Pydantic model for user documents.
    Add fields as needed.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: str

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True


class MongoRepository:
    """
    Generic repository class to manage MongoDB collections and CRUD operations.
    """

    def __init__(self, client: MongoClient, db_name: str, collection_name: str):
        self.client = client
        self.db = self.client[db_name]
        self.collection: collection.Collection = self.db[collection_name]

    def get_collection(self) -> collection.Collection:
        return self.collection

    # Example method
    def find_by_id(self, id: str) -> dict | None:
        if not ObjectId.is_valid(id):
            raise ValueError("Invalid ObjectId")
        return self.collection.find_one({"_id": ObjectId(id)})


class UserRepository(MongoRepository):
    """
    User-specific repository wrapping user collection operations.
    """

    def __init__(self, client: MongoClient, db_name: str):
        super().__init__(client, db_name, USER_COLLECTION_NAME)

    async def find_user_by_id(self, id: str) -> dict | None:
        # This method could be async if using motor (async driver)
        if not ObjectId.is_valid(id):
            raise ValueError("Invalid ObjectId")
        return self.collection.find_one({"_id": ObjectId(id)})

    # Add more user-specific DB methods here
