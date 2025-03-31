from typing import Callable, Dict, List, Optional, Union
from flask import request, jsonify
from src.utils.constants import ALLOW_COMMON_FILE_TYPE, LIMIT_COMMON_FILE_SIZE
from src.utils.api_error import ApiError
from asgiref.sync import async_to_sync
import asyncio

class ImageUploadConfig:
    def __init__(
        self,
        allowed_types: Optional[List[str]] = None,
        max_size: Optional[int] = None,
        field_name: str = "image"
    ):
        self.allowed_types = allowed_types or ALLOW_COMMON_FILE_TYPE
        self.max_size = max_size or LIMIT_COMMON_FILE_SIZE
        self.field_name = field_name

class ImageUploader:
    def __init__(self, config: Optional[ImageUploadConfig] = None):
        self.config = config or ImageUploadConfig()

    def single(self, field_name: str) -> Callable:
        """Configure middleware to handle single file upload"""
        self.config.field_name = field_name
        return self._handle_upload

    def _handle_upload(self, handler: Callable) -> Callable:
        """Handle the file upload and validation"""
        def wrapper(*args, **kwargs):
            try:
                # Get file from request
                file = request.files.get(self.config.field_name)
                
                # Only validate if file exists
                if file:
                    # Check file type
                    if file.content_type not in self.config.allowed_types:
                        raise ApiError(
                            415,
                            f"Image type is invalid. Only accept {', '.join(self.config.allowed_types)}"
                        )

                    # Check file size
                    file.seek(0, 2)  # Seek to end of file
                    file_size = file.tell()  # Get file size
                    file.seek(0)  # Reset file pointer
                    
                    if file_size > self.config.max_size:
                        raise ApiError(
                            413,
                            f"Image size exceeds limit of {self.config.max_size / (1024*1024)}MB"
                        )

                    # Add validated file to kwargs for the handler
                    kwargs['user_avatar_file'] = file

                # Call the handler
                if asyncio.iscoroutinefunction(handler):
                    return async_to_sync(handler)(*args, **kwargs)
                return handler(*args, **kwargs)

            except ApiError as e:
                return jsonify({"message": e.message}), e.status_code
            except Exception as e:
                return jsonify({"message": str(e)}), 500

        return wrapper

# Create uploader instance
uploader = ImageUploader()

# Export the uploader
image_upload_middleware = {
    "upload": uploader
}