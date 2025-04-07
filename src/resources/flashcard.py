from flask import request, jsonify, g
from src.repositories.flashcard import FlashcardRepository
from src.utils.api_error import ApiError
from src.utils.error_handlers import api_error_handler
from src.validation.flashcard import SaveFlashcardsValidation
import logging
import json

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
            
        # Validate request data
        validated_data = SaveFlashcardsValidation(**request.json)
        request_data = validated_data.model_dump()
        
        # Call repository method
        result = FlashcardRepository.save_flashcards_to_folder(
            create_new_folder=request_data["create_new_folder"],
            folder_id=request_data["folder_id"],
            folder_title=request_data["folder_title"],
            flashcards_data=request_data["flashcards"],
            user_id=user_id
        )
        
        return jsonify(result)

    @staticmethod
    @api_error_handler
    def import_flashcards():
        """Import flashcards from JSON file"""
        logger = logging.getLogger(__name__)
        logger.info("=== Importing Flashcards ===")
        
        # Validate request data
        if "file" not in request.files:
            raise ApiError(400, "No file uploaded")
        
        file = request.files["file"]
        if file.filename == "":
            raise ApiError(400, "No file selected")
        
        if not file.filename.endswith(".json"):
            raise ApiError(400, "Only JSON files are allowed")
        
        # Read and parse JSON file
        try:
            flashcards_data = json.load(file)
            logger.info(f"Successfully parsed JSON file with {len(flashcards_data)} flashcards")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file: {str(e)}")
            raise ApiError(400, "Invalid JSON file")
        
        # Get folder info from request
        create_new_folder = request.form.get("create_new_folder", "false").lower() == "true"
        folder_id = request.form.get("folder_id")
        folder_title = request.form.get("folder_title", "Imported Flashcards")
        
        # Get user ID from authenticated user
        user_id = g.user["_id"]
        
        # Save flashcards to folder
        result = FlashcardRepository.save_flashcards_to_folder(
            create_new_folder,
            folder_id,
            folder_title,
            flashcards_data,
            user_id
        )
        
        return jsonify({
            "message": "Flashcards imported successfully",
            "result": result
        }), 201