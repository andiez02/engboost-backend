from flask import Blueprint, request, jsonify
from resources.flashcard import FlashcardService

flashcard_bp = Blueprint('flashcard', __name__)

@flashcard_bp.route('/flashcards', methods=['POST'])
def create_flashcard():
    data = request.get_json()
    question = data.get('question')
    answer = data.get('answer')

    flashcard_service = FlashcardService()
    flashcard_id = flashcard_service.create_flashcard(question, answer)

    return jsonify({"flashcard_id": str(flashcard_id)}), 201

@flashcard_bp.route('/flashcards', methods=['GET'])
def get_flashcards():
    flashcard_service = FlashcardService()
    flashcards = flashcard_service.get_all_flashcards()

    flashcards_list = [{"question": card["question"], "answer": card["answer"]} for card in flashcards]
    return jsonify(flashcards_list), 200
