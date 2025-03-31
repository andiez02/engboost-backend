from src.models.folder import FolderModel
from src.models.flashcard import FlashcardModel
from src.utils.api_error import ApiError
from src.utils.error_handlers import repo_error_handler
from src.utils.mongo_helper import serialize_mongo_data
import logging
import asyncio

class FolderRepository:
    @staticmethod
    @repo_error_handler
    def create_new(folder_data):
        """Create a new folder"""
        logger = logging.getLogger(__name__)
        logger.info("=== Repository: Creating new folder ===")
        logger.info(f"Input folder data: {folder_data}")
        
        # Kiểm tra dữ liệu đầu vào
        if not folder_data.get("title"):
            logger.error("Folder title is missing")
            raise ValueError("Folder title is required")
            
        # Tạo folder mới
        logger.info("Calling FolderModel.create_new")
        folder_id = FolderModel.create_new(folder_data)
        logger.info(f"Folder created with ID: {folder_id}")
        
        # Lấy thông tin folder vừa tạo
        logger.info(f"Fetching new folder with ID: {folder_id}")
        new_folder = FolderModel.find_by_id(folder_id)
        logger.info(f"Fetched folder: {new_folder}")
        
        if new_folder is None:
            logger.error(f"Could not find newly created folder with ID: {folder_id}")
        
        serialized_folder = serialize_mongo_data(new_folder)
        logger.info(f"Serialized folder: {serialized_folder}")
        
        return serialized_folder


    @staticmethod
    @repo_error_handler
    def get_folders_by_user(user_id):
        """Get all folders by user ID"""
        logger = logging.getLogger(__name__)
        logger.info(f"=== Repository: Getting folders for user {user_id} ===")
        
        # Lấy danh sách folder
        logger.info(f"Calling FolderModel.find_by_user with user_id: {user_id}")
        folders = FolderModel.find_by_user(user_id)
        logger.info(f"Raw folders from database: {folders}")
        
        # Chuyển đổi ObjectId thành string
        logger.info("Serializing folder data")
        serialized_folders = [serialize_mongo_data(folder) for folder in folders]
        logger.info(f"Serialized folders: {serialized_folders}")
        
        return serialized_folders



    @staticmethod
    @repo_error_handler
    def get_folder_by_id(folder_id, user_id=None):
        """Get folder by ID"""
        folder = FolderModel.find_by_id(folder_id)
        
        if not folder:
            raise ApiError(404, "Folder not found")
            
        # Kiểm tra quyền truy cập nếu user_id được cung cấp
        if user_id and folder["user_id"] != user_id and not folder.get("is_public", False):
            raise ApiError(403, "You don't have permission to access this folder")
            
        return serialize_mongo_data(folder)

    @staticmethod
    @repo_error_handler
    def update_folder(folder_id, update_data, user_id):
        """Update folder"""
        # Kiểm tra folder tồn tại
        folder = FolderModel.find_by_id(folder_id)
        
        if not folder:
            raise ApiError(404, "Folder not found")
            
        # Kiểm tra quyền cập nhật
        if folder["user_id"] != user_id:
            raise ApiError(403, "You don't have permission to update this folder")
            
        # Cập nhật folder
        updated_folder = FolderModel.update(folder_id, update_data)
        
        return serialize_mongo_data(updated_folder)

    @staticmethod
    @repo_error_handler
    def delete_folder(folder_id, user_id):
        """Delete folder"""
        # Kiểm tra folder tồn tại
        folder = FolderModel.find_by_id(folder_id)
        
        if not folder:
            raise ApiError(404, "Folder not found")
            
        # Kiểm tra quyền xóa
        if folder["user_id"] != user_id:
            raise ApiError(403, "You don't have permission to delete this folder")
            
        # Xóa tất cả flashcard thuộc folder trước
        try:
            # Create event loop for async operation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(FlashcardModel.delete_by_folder(folder_id))
            loop.close()
        except Exception as e:
            logging.error(f"Error deleting flashcards for folder {folder_id}: {str(e)}")
            raise ApiError(500, "Error deleting flashcards")

        # Xóa folder
        deleted_folder = FolderModel.delete(folder_id)
        
        return serialize_mongo_data(deleted_folder)
