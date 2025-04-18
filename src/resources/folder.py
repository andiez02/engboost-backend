from flask import request, jsonify, g
from src.repositories.folder import FolderRepository
from src.utils.api_error import ApiError
from src.utils.error_handlers import api_error_handler
from src.validation.folder import CreateFolderValidation, UpdateFolderValidation
import logging
import asyncio

class FolderResource:
    @staticmethod
    @api_error_handler
    def create_folder():
        """Create a new folder"""
        # Validate request body
        validated_data = CreateFolderValidation(**request.json)
        request_data = validated_data.model_dump()
        
        # Add user_id from authenticated user
        request_data["user_id"] = g.user["_id"]
        
        # Create folder
        result = FolderRepository.create_new(request_data)
        
        return jsonify({
            "message": "Folder created successfully",
            "folder": result
        }), 201

    @staticmethod
    @api_error_handler
    def get_user_folders():
        """Get all folders for current user"""
        logger = logging.getLogger(__name__)
        logger.info("=== Getting User Folders ===")
        
        # Get user ID from authenticated user
        user_id = g.user.get("_id")
        logger.info(f"User ID from token: {user_id}")
        
        if not user_id:
            logger.error("No user_id found in g.user")
            raise ApiError(401, "Invalid authentication token")
        
        # Get folders
        logger.info(f"Calling FolderRepository.get_folders_by_user with user_id: {user_id}")
        result = FolderRepository.get_folders_by_user(user_id)
        logger.info(f"Found {len(result)} folders for user")
        
        response_data = {"folders": result}
        logger.info(f"Returning response: {response_data}")
        return jsonify(response_data), 200

    @staticmethod
    @api_error_handler
    def get_folder(folder_id):
        """Get folder by ID"""
        # Get user ID from authenticated user
        user_id = g.user["_id"]
        
        # Get folder
        result = FolderRepository.get_folder_by_id(folder_id, user_id)
        
        return jsonify(result), 200

    @staticmethod
    @api_error_handler
    def update_folder(folder_id):
        """Update folder"""
        # Validate request body
        validated_data = UpdateFolderValidation(**request.json)
        request_data = validated_data.model_dump(exclude_none=True)
        
        # Get user ID from authenticated user
        user_id = g.user["_id"]
        
        # Update folder
        result = FolderRepository.update_folder(folder_id, request_data, user_id)
        
        return jsonify({
            "message": "Folder updated successfully",
            "folder": result
        }), 200

    @staticmethod
    @api_error_handler
    def delete_folder(folder_id):
        """Delete folder"""
        # Get user ID from authenticated user
        user_id = g.user["_id"]
        
        # Delete folder
        result = FolderRepository.delete_folder(folder_id, user_id)
        
        return jsonify({
            "message": "Folder deleted successfully",
            "folder": result
        }), 200

    @staticmethod
    @api_error_handler
    def get_public_folders():
        """Get all public folders"""
        logger = logging.getLogger(__name__)
        logger.info("=== Getting Public Folders ===")
        
        # Get query parameters
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 100))
        
        # Get folders
        result = FolderRepository.get_public_folders(skip, limit)
        
        return jsonify({
            "folders": result
        }), 200

    @staticmethod
    @api_error_handler
    def make_folder_public(folder_id):
        """Toggle folder public state (admin only)"""
        # Get user ID from authenticated user
        user_id = g.user["_id"]
        
        # Update folder to toggle public state
        result = FolderRepository.toggle_folder_public(folder_id, user_id)
        
        return jsonify({
            "message": "Folder public state toggled successfully",
            "folder": result
        }), 200
