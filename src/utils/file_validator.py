import os
import logging
from werkzeug.utils import secure_filename
from src.utils.api_error import ApiError

logger = logging.getLogger(__name__)

class FileValidator:
    # Định dạng file cho phép
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'wmv', 'mkv', 'webm'}
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    
    # Giới hạn kích thước file (byte)
    MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
    MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10MB
    
    @staticmethod
    def allowed_video_file(filename):
        """Kiểm tra xem file có phải là định dạng video cho phép không"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileValidator.ALLOWED_VIDEO_EXTENSIONS
    
    @staticmethod
    def allowed_image_file(filename):
        """Kiểm tra xem file có phải là định dạng ảnh cho phép không"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileValidator.ALLOWED_IMAGE_EXTENSIONS
    
    @staticmethod
    def validate_video(file):
        """Kiểm tra tính hợp lệ của file video"""
        logger = logging.getLogger(__name__)
        
        if not file:
            raise ApiError(400, "No video file provided")
        
        logger.info("Validating video file: %s", file.filename)
        logger.info("Video file info - content_type: %s, size: %s bytes", 
                  file.content_type, file.content_length if hasattr(file, 'content_length') else 'unknown')
        
        filename = secure_filename(file.filename)
        
        # Kiểm tra định dạng
        if not FileValidator.allowed_video_file(filename):
            allowed_extensions = ', '.join(FileValidator.ALLOWED_VIDEO_EXTENSIONS)
            raise ApiError(400, f"Video file format not allowed. Allowed formats: {allowed_extensions}")
        
        # Kiểm tra kích thước
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset vị trí con trỏ file về đầu
        
        logger.info("Video file size calculated: %s bytes", file_size)
        
        if file_size > FileValidator.MAX_VIDEO_SIZE:
            max_size_mb = FileValidator.MAX_VIDEO_SIZE / (1024 * 1024)
            raise ApiError(400, f"Video file too large. Maximum size: {max_size_mb}MB")
        
        return True
    
    @staticmethod
    def validate_image(file):
        """Kiểm tra tính hợp lệ của file ảnh"""
        if not file:
            raise ApiError(400, "No image file provided")
        
        filename = secure_filename(file.filename)
        
        # Kiểm tra định dạng
        if not FileValidator.allowed_image_file(filename):
            allowed_extensions = ', '.join(FileValidator.ALLOWED_IMAGE_EXTENSIONS)
            raise ApiError(400, f"Image file format not allowed. Allowed formats: {allowed_extensions}")
        
        # Kiểm tra kích thước
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset vị trí con trỏ file về đầu
        
        if file_size > FileValidator.MAX_IMAGE_SIZE:
            max_size_mb = FileValidator.MAX_IMAGE_SIZE / (1024 * 1024)
            raise ApiError(400, f"Image file too large. Maximum size: {max_size_mb}MB")
        
        return True 