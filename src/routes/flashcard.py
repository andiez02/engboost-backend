from flask import Blueprint
from src.resources.flashcard import FlashcardResource
from src.middleware.auth_middleware import is_authorized

flashcard_bp = Blueprint("flashcard", __name__)

flashcard_bp.route("/flashcards/save-to-folder", methods=["POST"])(is_authorized(FlashcardResource.save_flashcards_to_folder))

flashcard_bp.route("/folders/<folder_id>/flashcards", methods=["GET"])(is_authorized(FlashcardResource.get_flashcards_by_folder))
flashcard_bp.route("/flashcards/<flashcard_id>", methods=["GET"])(is_authorized(FlashcardResource.get_flashcard_by_id))
flashcard_bp.route("/flashcards/<flashcard_id>", methods=["DELETE"])(is_authorized(FlashcardResource.delete_flashcard))
