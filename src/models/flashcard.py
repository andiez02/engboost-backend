from pydantic import BaseModel, Field, validator, field_validator
from datetime import datetime
from bson import ObjectId
from src.config.mongodb import MongoDB
from src.utils.api_error import ApiError
from src.utils.error_handlers import model_error_handler
import logging
from pymongo import ReturnDocument
import asyncio
from concurrent.futures import ThreadPoolExecutor

class FlashcardSchemaDB(BaseModel):
    english: str = Field(..., min_length=1, max_length=200)
    vietnamese: str = Field(..., min_length=1, max_length=200)
    object: str | None = None
    image_url: str | None = None  # Store Cloudinary URL directly
    folder_id: str
    user_id: str
    is_public: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    @field_validator('english', 'vietnamese')
    @classmethod
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError('Field cannot be empty')
        return v

    class Config:
        from_attributes = True

class FlashcardModel:
    FLASHCARD_COLLECTION_NAME = MongoDB.get_db()["flashcards"]
    
    FLASHCARD_COLLECTION_NAME.create_index("folder_id")
    FLASHCARD_COLLECTION_NAME.create_index("user_id")

    @classmethod
    @model_error_handler
    def find_by_folder(cls, folder_id, skip=0, limit=100):
        if not ObjectId.is_valid(folder_id):
            raise ApiError(400, "Invalid folder ID format")
        
        query = {"folder_id": folder_id}
        cursor = cls.FLASHCARD_COLLECTION_NAME.find(query).sort("created_at", -1).skip(skip).limit(limit)
        return list(cursor)

    @classmethod
    @model_error_handler
    def find_by_id(cls, flashcard_id):
        if not ObjectId.is_valid(flashcard_id):
            raise ApiError(400, "Invalid flashcard ID format")

        query = {"_id": ObjectId(flashcard_id)}
        flashcard = cls.FLASHCARD_COLLECTION_NAME.find_one(query)
        
        if not flashcard:
            raise ApiError(404, "Flashcard not found")
            
        return flashcard

    @classmethod
    @model_error_handler
    def delete(cls, flashcard_id):
        if not ObjectId.is_valid(flashcard_id):
            raise ApiError(400, "Invalid flashcard ID format")

        flashcard = cls.FLASHCARD_COLLECTION_NAME.find_one({"_id": ObjectId(flashcard_id)})
        if not flashcard:
            raise ApiError(404, "Flashcard not found")
            
        result = cls.FLASHCARD_COLLECTION_NAME.find_one_and_delete(
            {"_id": ObjectId(flashcard_id)}
        )
        
        if result:
            from src.models.folder import FolderModel
            FolderModel.increment_flashcard_count(result["folder_id"], increment=-1)
            
        return result

    @classmethod
    @model_error_handler
    async def delete_by_folder(cls, folder_id):
        """Delete all flashcards in a folder asynchronously"""
        if not ObjectId.is_valid(folder_id):
            raise ApiError(400, "Invalid folder ID format")
            
        # First, delete all flashcards in a single operation
        result = cls.FLASHCARD_COLLECTION_NAME.delete_many({"folder_id": folder_id})
        deleted_count = result.deleted_count
        
        if deleted_count > 0:
            # Get deleted flashcards for image cleanup
            deleted_flashcards = list(cls.FLASHCARD_COLLECTION_NAME.find({
                "folder_id": folder_id,
                "image_url": {"$exists": True}
            }))
            
            # Create a thread pool for handling Cloudinary operations
            with ThreadPoolExecutor() as executor:
                # Delete images from Cloudinary concurrently
                from src.config.cloudinary import CloudinaryService
                delete_tasks = []
                for flashcard in deleted_flashcards:
                    if flashcard.get("image_url"):
                        delete_tasks.append(
                            asyncio.get_event_loop().run_in_executor(
                                executor,
                                CloudinaryService.delete_image,
                                flashcard["image_url"]
                            )
                        )
                
                # Wait for all image deletions to complete
                if delete_tasks:
                    await asyncio.gather(*delete_tasks)
        
        return deleted_count

    @classmethod
    @model_error_handler
    def bulk_insert(cls, flashcards):
        """Bulk insert flashcards"""
        if not flashcards:
            return {"inserted_count": 0}
                
        result = cls.FLASHCARD_COLLECTION_NAME.insert_many(flashcards)
        return {"inserted_count": len(result.inserted_ids)}

    @classmethod
    @model_error_handler
    async def make_all_public_by_folder(cls, folder_id, is_public):
        """Update all flashcards in a folder public state"""
        if not ObjectId.is_valid(folder_id):
            raise ApiError(400, "Invalid folder ID format")
            
        # Update all flashcards in the folder to public state
        result = cls.FLASHCARD_COLLECTION_NAME.update_many(
            {"folder_id": folder_id},
            {
                "$set": {
                    "is_public": is_public,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count

    @classmethod
    @model_error_handler
    def count_by_folder(cls, folder_id):
        """Count flashcards in a folder"""
        logger = logging.getLogger(__name__)
        logger.info(f"=== Model: Counting flashcards in folder {folder_id} ===")
        
        if not ObjectId.is_valid(folder_id):
            raise ApiError(400, "Invalid folder ID format")
        
        query = {"folder_id": folder_id}
        count = cls.FLASHCARD_COLLECTION_NAME.count_documents(query)
        logger.info(f"Found {count} flashcards in folder {folder_id}")
        
        return count

