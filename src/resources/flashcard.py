from flask import request, jsonify, g
from src.repositories.flashcard import FlashcardRepository
from src.utils.api_error import ApiError
from src.utils.error_handlers import api_error_handler
import logging

class FlashcardResource:
    @staticmethod
    @api_error_handler
    def get_flashcards_by_folder(folder_id):
        """Get all flashcards in a folder"""
        user_id = g.user["_id"]
        flashcards = FlashcardRepository.get_flashcards_by_folder(folder_id, user_id)
        return jsonify(flashcards)

    @staticmethod
    @api_error_handler
    def get_flashcard_by_id(flashcard_id):
        """Get a single flashcard by ID"""
        user_id = g.user["_id"]
        flashcard = FlashcardRepository.get_flashcard_by_id(flashcard_id, user_id)
        return jsonify(flashcard)

    @staticmethod
    @api_error_handler
    def delete_flashcard(flashcard_id):
        """Delete a flashcard"""
        user_id = g.user["_id"]
        deleted_flashcard = FlashcardRepository.delete_flashcard(flashcard_id, user_id)
        return jsonify(deleted_flashcard)

    @staticmethod
    @api_error_handler
    def save_flashcards_to_folder():
        """Save flashcards to a folder (new or existing)"""
        user_id = g.user["_id"]
        
        # Check if request has JSON content
        if not request.is_json:
            raise ApiError(400, "Request must have JSON content type")
            
        data = request.get_json()
        if not data:
            raise ApiError(400, "Request body cannot be empty")
        
        # Log request data for debugging
        logging.info(f"Save to folder request data: {data}")
            
        # Extract and validate parameters
        create_new_folder = data.get("create_new_folder", False)
        folder_id = data.get("folder_id")
        folder_title = data.get("folder_title")
        flashcards_data = data.get("flashcards", [])
        
        # Validate flashcards
        if not flashcards_data or not isinstance(flashcards_data, list):
            raise ApiError(400, "Flashcards must be a non-empty list")
        
        # Validate folder information
        if create_new_folder:
            if not folder_title or not folder_title.strip():
                raise ApiError(400, "Folder title is required when creating a new folder")
        else:
            if not folder_id:
                raise ApiError(400, "Folder ID is required when using existing folder")
        
        # Call repository method
        result = FlashcardRepository.save_flashcards_to_folder(
            create_new_folder=create_new_folder,
            folder_id=folder_id,
            folder_title=folder_title,
            flashcards_data=flashcards_data,
            user_id=user_id
        )
        
        return jsonify(result)