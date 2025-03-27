from pydantic import BaseModel, Field, validator
from datetime import datetime
from bson import ObjectId
from src.config.mongodb import MongoDB
from src.utils.api_error import ApiError
from src.utils.error_handlers import model_error_handler
import re
import logging

class FolderSchemaDB(BaseModel):
    title: str = Field(..., min_length=1, max_length=30)
    user_id: str  # ID của người tạo folder
    flashcard_count: int = Field(default=0)  # Số lượng flashcard trong folder
    is_public: bool = Field(default=False)  # Folder có công khai không
    
    # Auto-generated fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    _destroy: bool = False

    @validator('title')
    def title_format(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v

    class Config:
        from_attributes = True

class FolderModel:
    ### Define Collection
    FOLDER_COLLECTION_NAME = MongoDB.get_db()["folders"]
    
    # Tạo index cho user_id để tối ưu tìm kiếm
    FOLDER_COLLECTION_NAME.create_index("user_id")

    @classmethod
    @model_error_handler
    def create_new(cls, folder_data):
        """Create a new folder"""
        logger = logging.getLogger(__name__)
        logger.info(f"=== Model: Creating new folder ===")
        logger.info(f"Input data: {folder_data}")
        
        try:
            validated_folder = FolderSchemaDB(**folder_data)
            logger.info(f"Validated folder data: {validated_folder.model_dump()}")
            
            result = cls.FOLDER_COLLECTION_NAME.insert_one(validated_folder.model_dump())
            logger.info(f"Insert result: {result.inserted_id}")
            
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            raise



    @classmethod
    @model_error_handler
    def find_by_user(cls, user_id):
        """Find all folders by user ID"""
        logger = logging.getLogger(__name__)
        logger.info(f"=== Model: Finding folders for user {user_id} ===")
        logger.info(f"User ID type: {type(user_id)}")
        
        # Đảm bảo user_id là string khi query
        if isinstance(user_id, ObjectId):
            user_id = str(user_id)
        
        query = {"user_id": user_id}
        logger.info(f"MongoDB query: {query}")
        
        cursor = cls.FOLDER_COLLECTION_NAME.find(query).sort("created_at", -1)
        result = list(cursor)
        logger.info(f"Query returned {len(result)} folders")
        
        # Log first folder for debugging if available
        if result and len(result) > 0:
            logger.info(f"First folder sample: {result[0]}")
        
        return result



    @classmethod
    @model_error_handler
    def find_by_id(cls, folder_id):
        """Find folder by ID"""
        logger = logging.getLogger(__name__)
        logger.info(f"=== Model: Finding folder by ID: {folder_id} ===")
        
        if not ObjectId.is_valid(folder_id):
            logger.error(f"Invalid folder ID format: {folder_id}")
            raise ApiError(400, "Invalid folder ID")

        # Bỏ điều kiện _destroy để kiểm tra
        query = {"_id": ObjectId(folder_id)}
        logger.info(f"MongoDB query: {query}")
        
        folder = cls.FOLDER_COLLECTION_NAME.find_one(query)
        logger.info(f"Query result: {folder}")
        
        if folder:
            folder["_id"] = str(folder["_id"])
            logger.info(f"Converted _id to string: {folder['_id']}")
        else:
            logger.warning(f"No folder found with ID: {folder_id}")
            
        return folder


    @classmethod
    @model_error_handler
    def update(cls, folder_id, update_data):
        """Update folder data"""
        if not ObjectId.is_valid(folder_id):
            raise ApiError(400, "Invalid folder ID")
        
        # Remove invalid update fields
        INVALID_UPDATE_FIELDS = ["_id", "user_id", "created_at", "flashcard_count"]
        update_data = {k: v for k, v in update_data.items() if k not in INVALID_UPDATE_FIELDS}

        # Update updatedAt field
        update_data["updated_at"] = datetime.utcnow()

        result = cls.FOLDER_COLLECTION_NAME.find_one_and_update(
            {"_id": ObjectId(folder_id), "_destroy": False},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            result["_id"] = str(result["_id"])
        return result

    @classmethod
    @model_error_handler
    def delete(cls, folder_id):
        """Soft delete a folder"""
        if not ObjectId.is_valid(folder_id):
            raise ApiError(400, "Invalid folder ID")

        result = cls.FOLDER_COLLECTION_NAME.find_one_and_update(
            {"_id": ObjectId(folder_id)},
            {"$set": {"_destroy": True, "updated_at": datetime.utcnow()}},
            return_document=True
        )
        
        if result:
            result["_id"] = str(result["_id"])
        return result

    @classmethod
    @model_error_handler
    def increment_flashcard_count(cls, folder_id, increment=1):
        """Increment or decrement flashcard count"""
        if not ObjectId.is_valid(folder_id):
            raise ApiError(400, "Invalid folder ID")

        result = cls.FOLDER_COLLECTION_NAME.find_one_and_update(
            {"_id": ObjectId(folder_id), "_destroy": False},
            {
                "$inc": {"flashcard_count": increment},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True
        )
        
        if result:
            result["_id"] = str(result["_id"])
        return result
