from pydantic import BaseModel, EmailStr, constr, Field
from datetime import datetime
import uuid
from bson import ObjectId
from src.config.mongodb import MongoDB

class UserSchemaDB(BaseModel):
    email: EmailStr
    password: constr(min_length=6)
    
    # Auto-generated fields
    username: str = Field(default_factory=lambda: "")  
    avatar: str | None = None
    role: str = Field(default="CLIENT", pattern="^(CLIENT|ADMIN)$")
    isActive: bool = False
    verifyToken: str = Field(default_factory=lambda: str(uuid.uuid4()))
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime | None = None
    _destroy: bool = False

    class Config:
        from_attributes = True

class UserModel:
    ### Define Collection
    USER_COLLECTION_NAME = MongoDB.get_db()["users"]

    @classmethod
    def create_new(cls, user_data):
        """Validate before saving to DB"""
        validated_user = UserSchemaDB(**user_data)  # Validate again
        result = cls.USER_COLLECTION_NAME.insert_one(validated_user.model_dump())
        return str(result.inserted_id)

    @classmethod
    def find_by_email(cls, email):
        return cls.USER_COLLECTION_NAME.find_one({"email": email})

    @classmethod
    def find_one_by_id(cls, user_id):
        """Finds a user by ID and converts _id to string"""
        if not ObjectId.is_valid(user_id):
            return None

        user = cls.USER_COLLECTION_NAME.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return user
