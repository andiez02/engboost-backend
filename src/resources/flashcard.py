from repositories.flashcard import FlashcardRepository
from models.flashcard import Flashcard

class FlashcardService:
    def __init__(self):
        self.repository = FlashcardRepository()

    def create_flashcard(self, question, answer):
        flashcard = Flashcard(question, answer)
        flashcard_id = self.repository.create_flashcard(flashcard)
        return flashcard_id

    def get_all_flashcards(self):
        flashcards = self.repository.get_all_flashcards()
        return flashcards
