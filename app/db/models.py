from pymongo import MongoClient
from bson import ObjectId

# Used for typing and ensuring ObjectId is valid
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

# Collection initialization
def get_user_collection(db):
    return db.get_collection("users")
