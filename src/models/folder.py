from pydantic import BaseModel, Field, validator
from datetime import datetime
from bson import ObjectId
from src.config.mongodb import MongoDB
from src.utils.api_error import ApiError
from src.utils.error_handlers import model_error_handler
import re
import logging
from pymongo import ReturnDocument


class FolderSchemaDB(BaseModel):
    title: str = Field(..., min_length=1, max_length=30)
    user_id: str  # ID của người tạo folder
    flashcard_count: int = Field(default=0)  
    is_public: bool = Field(default=False) 
    
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
    # Tạo index cho title và user_id để đảm bảo tên folder không trùng lặp cho mỗi user
    FOLDER_COLLECTION_NAME.create_index([("title", 1), ("user_id", 1)], unique=True)

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
            
            # Kiểm tra xem folder với title này đã tồn tại chưa
            existing_folder = cls.FOLDER_COLLECTION_NAME.find_one({
                "title": validated_folder.title,
                "user_id": validated_folder.user_id
            })
            
            if existing_folder:
                logger.error(f"Folder with title '{validated_folder.title}' already exists for user {validated_folder.user_id}")
                raise ApiError(400, f"Folder with title '{validated_folder.title}' already exists")
            
            result = cls.FOLDER_COLLECTION_NAME.insert_one(validated_folder.model_dump())
            logger.info(f"Insert result: {result.inserted_id}")
            
            return str(result.inserted_id)
        except ApiError as e:
            # Re-raise ApiError để giữ nguyên status code và message
            raise
        except Exception as e:
            # Kiểm tra lỗi trùng lặp từ MongoDB (duplicate key error)
            if "duplicate key error" in str(e) and "title" in str(e):
                logger.error(f"Duplicate folder title error: {str(e)}")
                raise ApiError(400, f"Folder with this title already exists")
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
        logger = logging.getLogger(__name__)
        logger.info(f"=== Model: Updating folder {folder_id} ===")
        logger.info(f"Update data: {update_data}")
        
        if not ObjectId.is_valid(folder_id):
            raise ApiError(400, "Invalid folder ID")
        
        # Remove invalid update fields
        INVALID_UPDATE_FIELDS = ["_id", "user_id", "created_at", "flashcard_count"]
        update_data = {k: v for k, v in update_data.items() if k not in INVALID_UPDATE_FIELDS}

        # Update updatedAt field
        update_data["updated_at"] = datetime.utcnow()
        
        # Nếu có cập nhật title, kiểm tra xem title mới có trùng với folder khác không
        if "title" in update_data:
            # Lấy thông tin folder hiện tại
            current_folder = cls.FOLDER_COLLECTION_NAME.find_one({"_id": ObjectId(folder_id)})
            if not current_folder:
                raise ApiError(404, "Folder not found")
            
            # Kiểm tra xem title mới có khác với title cũ không
            if update_data["title"] != current_folder["title"]:
                # Kiểm tra xem title mới có trùng với folder khác của cùng user không
                existing_folder = cls.FOLDER_COLLECTION_NAME.find_one({
                    "title": update_data["title"],
                    "user_id": current_folder["user_id"],
                    "_id": {"$ne": ObjectId(folder_id)}  # Loại trừ folder hiện tại
                })
                
                if existing_folder:
                    logger.error(f"Folder with title '{update_data['title']}' already exists for user {current_folder['user_id']}")
                    raise ApiError(400, f"Folder with title '{update_data['title']}' already exists")

        try:
            result = cls.FOLDER_COLLECTION_NAME.find_one_and_update(
                {"_id": ObjectId(folder_id)},
                {"$set": update_data},
                return_document=ReturnDocument.AFTER
            )
            
            if result:
                result["_id"] = str(result["_id"])
                logger.info(f"Updated folder: {result}")
            else:
                logger.warning(f"No folder found with ID: {folder_id}")
                
            return result
        except Exception as e:
            # Kiểm tra lỗi trùng lặp từ MongoDB (duplicate key error)
            if "duplicate key error" in str(e) and "title" in str(e):
                logger.error(f"Duplicate folder title error: {str(e)}")
                raise ApiError(400, f"Folder with this title already exists")
            logger.error(f"Error updating folder: {str(e)}")
            raise
    
    @classmethod
    @model_error_handler
    def delete(cls, folder_id):
        """Permanently delete a folder from database"""
        if not ObjectId.is_valid(folder_id):
            raise ApiError(400, "Invalid folder ID")

        # Xóa vĩnh viễn folder khỏi database
        result = cls.FOLDER_COLLECTION_NAME.find_one_and_delete(
            {"_id": ObjectId(folder_id)}
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

        logging.info(f"Incrementing flashcard count for folder {folder_id} by {increment}")
        query = {"_id": ObjectId(folder_id)}
        logging.info(f"Query for updating folder: {query}")
        result = cls.FOLDER_COLLECTION_NAME.find_one_and_update(
            query,
            {
                "$inc": {"flashcard_count": increment},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=ReturnDocument.AFTER
        )
        
        if result:
            logging.info(f"Updated flashcard count for folder {folder_id}: {result['flashcard_count']}")
        else:
            logging.error(f"Failed to update flashcard count for folder {folder_id}")

    @classmethod
    @model_error_handler
    def find_public_folders(cls, skip=0, limit=100):
        """Find all public folders"""
        logger = logging.getLogger(__name__)
        logger.info("=== Model: Finding public folders ===")
        
        query = {
            "is_public": True,
        }
        
        cursor = cls.FOLDER_COLLECTION_NAME.find(query).sort("created_at", -1).skip(skip).limit(limit)
        return list(cursor)

    @classmethod
    @model_error_handler
    def update_flashcard_count(cls, folder_id, count):
        """Update folder's flashcard count to an exact value"""
        logger = logging.getLogger(__name__)
        logger.info(f"=== Model: Updating folder {folder_id} flashcard_count to {count} ===")
        
        if not ObjectId.is_valid(folder_id):
            raise ApiError(400, "Invalid folder ID format")
        
        result = cls.FOLDER_COLLECTION_NAME.update_one(
            {"_id": ObjectId(folder_id)},
            {"$set": {"flashcard_count": count}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated folder {folder_id} flashcard_count to {count}")
        else:
            logger.error(f"Failed to update flashcard count for folder {folder_id}")
        
        return result.modified_count
