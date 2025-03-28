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
            
        # Get all flashcards in the folder
        flashcards = cls.find_by_folder(folder_id)
        
        # Create a thread pool for handling Cloudinary operations
        with ThreadPoolExecutor() as executor:
            # Delete images from Cloudinary concurrently
            from src.config.cloudinary import CloudinaryService
            delete_tasks = []
            for flashcard in flashcards:
                if flashcard.get("image_public_id"):
                    delete_tasks.append(
                        asyncio.get_event_loop().run_in_executor(
                            executor,
                            CloudinaryService.delete_image,
                            flashcard["image_public_id"]
                        )
                    )
            
            # Wait for all image deletions to complete
            if delete_tasks:
                await asyncio.gather(*delete_tasks)
        
        # Delete all flashcards
        result = cls.FLASHCARD_COLLECTION_NAME.delete_many({"folder_id": folder_id})
        return result.deleted_count

    @classmethod
    @model_error_handler
    def bulk_insert(cls, flashcards):
        """Bulk insert flashcards"""
        if not flashcards:
            return {"inserted_count": 0}
                
        result = cls.FLASHCARD_COLLECTION_NAME.insert_many(flashcards)
        return {"inserted_count": len(result.inserted_ids)}
