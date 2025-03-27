from datetime import datetime
from src.config.mongodb import MongoDB

class CourseModel:
    COLLECTION = MongoDB.get_db()["courses"]

    @classmethod
    def create(cls, course_data):
        course_data["createdAt"] = datetime.utcnow()
        result = cls.COLLECTION.insert_one(course_data)
        return str(result.inserted_id)

    @classmethod
    def find_all(cls):
        courses = cls.COLLECTION.find()
        return [{**c, "_id": str(c["_id"])} for c in courses]
