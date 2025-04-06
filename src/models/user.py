from pydantic import BaseModel, EmailStr, constr, Field
from datetime import datetime
import uuid
from bson import ObjectId
from src.config.mongodb import MongoDB
from src.utils.constants import (
    EMAIL_RULE,
    EMAIL_RULE_MESSAGE,
    PASSWORD_RULE,
    PASSWORD_RULE_MESSAGE,
)
from src.utils.api_error import ApiError

class UserSchemaDB(BaseModel):
    email: EmailStr = Field(..., pattern=EMAIL_RULE.pattern, description=EMAIL_RULE_MESSAGE)
    password: str = Field(..., min_length=8, description=PASSWORD_RULE_MESSAGE)

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
        try:
            validated_user = UserSchemaDB(**user_data) 
            result = cls.USER_COLLECTION_NAME.insert_one(validated_user.model_dump())
            return str(result.inserted_id)
        except Exception as e:
            raise ApiError(500, "An error occurred while creating a new user.") 

    @staticmethod
    def find_one_by_email(email):
        """Find user by email"""
        try:
            return UserModel.USER_COLLECTION_NAME.find_one({"email": email})
        except Exception as e:
            raise ApiError(500, "An error occurred while finding the user by email.")  

    @staticmethod
    def find_one_by_id(user_id):
        """Find user by ID and convert _id to string"""
        try:
            if not ObjectId.is_valid(user_id):
                raise ApiError(400, "Invalid user ID")

            user = UserModel.USER_COLLECTION_NAME.find_one({"_id": ObjectId(user_id)})
            if user:
                user["_id"] = str(user["_id"]) 
            return user
        except Exception as e:
            raise ApiError(500, "An error occurred while finding the user by ID.") 

    @classmethod
    def update(cls, user_id, update_data):
        """Update user data"""
        try:
            if not ObjectId.is_valid(user_id):
                raise ApiError(400, "Invalid user ID")
            
            # Remove invalid update fields if necessary
            INVALID_UPDATE_FIELDS = ["_id", "email", "createdAt"]  # Không cho phép cập nhật các trường này
            update_data = {k: v for k, v in update_data.items() if k not in INVALID_UPDATE_FIELDS}

            # Update field `updatedAt` khi có thay đổi
            update_data["updatedAt"] = datetime.utcnow()

            result = cls.USER_COLLECTION_NAME.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": update_data},
                return_document=True  # Trả về dữ liệu sau update
            )
            if result:
                result["_id"] = str(result["_id"])  # Convert ObjectId to string
            return result
        except Exception as e:
            raise ApiError(500, "An error occurred while updating the user data.")

    @classmethod
    def delete_one(cls, user_id):
        """
        Xóa một người dùng dựa trên ID.

        Args:
            user_id: ID của người dùng cần xóa

        Returns:
            Kết quả của thao tác xóa
        """
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        return cls.USER_COLLECTION_NAME.delete_one({"_id": user_id})