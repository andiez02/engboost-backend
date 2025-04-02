from src.models.flashcard import FlashcardModel
from src.models.folder import FolderModel
from src.utils.api_error import ApiError
from src.utils.error_handlers import repo_error_handler
from src.utils.mongo_helper import serialize_mongo_data
from src.config.cloudinary import CloudinaryService
import logging

class FlashcardRepository:
    @staticmethod
    @repo_error_handler
    def get_flashcards_by_folder(folder_id, user_id):
        folder = FolderModel.find_by_id(folder_id)
        if not folder:
            raise ApiError(404, "Folder not found")
            
        if folder["user_id"] != user_id and not folder.get("is_public", False):
            raise ApiError(403, "You don't have permission to access this folder")
            
        flashcards = FlashcardModel.find_by_folder(folder_id)
        serialized_flashcards = [serialize_mongo_data(flashcard) for flashcard in flashcards]
        
        return serialized_flashcards

    @staticmethod
    @repo_error_handler
    def get_flashcard_by_id(flashcard_id, user_id):
        flashcard = FlashcardModel.find_by_id(flashcard_id)
        folder = FolderModel.find_by_id(flashcard["folder_id"])
        if not folder:
            raise ApiError(404, "Folder not found")
            
        if folder["user_id"] != user_id and not folder.get("is_public", False):
            raise ApiError(403, "You don't have permission to access this flashcard")
            
        return serialize_mongo_data(flashcard)

    @staticmethod
    @repo_error_handler
    def delete_flashcard(flashcard_id, user_id):
        flashcard = FlashcardModel.find_by_id(flashcard_id)
        folder = FolderModel.find_by_id(flashcard["folder_id"])
        if folder["user_id"] != user_id:
            raise ApiError(403, "You don't have permission to delete this flashcard")
        
        if flashcard.get("image_url"):
            CloudinaryService.delete_image(flashcard["image_url"])
        
        # Xóa flashcard
        deleted_flashcard = FlashcardModel.delete(flashcard_id)
        
        # Đếm số lượng flashcard còn lại trong folder
        remaining_flashcards = FlashcardModel.count_by_folder(flashcard["folder_id"])
        
        # Cập nhật flashcard_count của folder dựa trên số lượng thực tế
        FolderModel.update_flashcard_count(flashcard["folder_id"], remaining_flashcards)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Updated folder {flashcard['folder_id']} flashcard_count to {remaining_flashcards}")
        
        return serialize_mongo_data(deleted_flashcard)

    @staticmethod
    @repo_error_handler
    def save_flashcards_to_folder(create_new_folder, folder_id, folder_title, flashcards_data, user_id):
        """Save flashcards to a folder"""
        logger = logging.getLogger(__name__)
        logger.info("=== Repository: Saving flashcards to folder ===")
        
        # Tạo folder mới nếu cần
        if create_new_folder:
            folder_data = {
                "title": folder_title,
                "user_id": user_id,
                "is_public": False,  # Đảm bảo folder mới luôn private
                "flashcard_count": 0  # Khởi tạo flashcard_count = 0
            }
            folder_id = FolderModel.create_new(folder_data)
            logger.info(f"Created new folder with ID: {folder_id}")
        
        # Kiểm tra folder tồn tại
        folder = FolderModel.find_by_id(folder_id)
        if not folder:
            raise ApiError(404, "Folder not found")
        
        # Kiểm tra quyền truy cập
        if folder["user_id"] != user_id:
            raise ApiError(403, "You don't have permission to add flashcards to this folder")
        
        # Chuẩn bị dữ liệu flashcard
        flashcards = []
        for flashcard_data in flashcards_data:
            flashcard = {
                "english": flashcard_data["english"],
                "vietnamese": flashcard_data["vietnamese"],
                "object": flashcard_data.get("object"),
                "image_url": flashcard_data.get("image_url"),
                "folder_id": folder_id,
                "user_id": user_id,
                "is_public": False  # Đảm bảo flashcard mới luôn private
            }
            flashcards.append(flashcard)
        
        # Lưu flashcards vào database
        if flashcards:
            FlashcardModel.bulk_insert(flashcards)
            logger.info(f"Saved {len(flashcards)} flashcards to folder {folder_id}")
            
            # Cập nhật flashcard_count của folder
            FolderModel.increment_flashcard_count(folder_id, increment=len(flashcards))
            logger.info(f"Updated folder {folder_id} flashcard_count: +{len(flashcards)}")
        
        # Serialize dữ liệu trước khi trả về
        serialized_flashcards = []
        for flashcard in flashcards:
            serialized_flashcard = serialize_mongo_data(flashcard)
            serialized_flashcards.append(serialized_flashcard)
        
        return {
            "folder_id": str(folder_id),  # Convert ObjectId to string
            "flashcards": serialized_flashcards
        }