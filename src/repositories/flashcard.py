from config.mongodb import get_db

class FlashcardRepository:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.flashcards  # Tên collection trong MongoDB

    def create_flashcard(self, flashcard):
        flashcard_data = {
            "question": flashcard.question,
            "answer": flashcard.answer
        }
        result = self.collection.insert_one(flashcard_data)
        return result.inserted_id

    def get_all_flashcards(self):
        flashcards = self.collection.find()
        return list(flashcards)
