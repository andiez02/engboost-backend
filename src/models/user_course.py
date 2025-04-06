from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from src.config.mongodb import MongoDB

class UserCourseSchemaDB(BaseModel):
    user_id: str
    course_id: str
    registered_at: datetime = Field(default_factory=datetime.utcnow)

class UserCourseModel:
    USER_COURSE_COLLECTION_NAME = MongoDB.get_db()["user_courses"]

    @classmethod
    def create_new(cls, user_id, course_id):
        """Tạo mới đăng ký khóa học"""
        user_course_data = {
            "user_id": user_id,
            "course_id": course_id,
            "registered_at": datetime.utcnow()
        }
        validated_data = UserCourseSchemaDB(**user_course_data).model_dump()
        result = cls.USER_COURSE_COLLECTION_NAME.insert_one(validated_data)
        return str(result.inserted_id)


    @classmethod
    def find_by_user_and_course(cls, user_id, course_id):
        """Tìm đăng ký khóa học theo user_id và course_id"""
        return cls.USER_COURSE_COLLECTION_NAME.find_one({
            "user_id": user_id,
            "course_id": course_id
        })


    @classmethod
    def find_by_user(cls, user_id):
        """Tìm tất cả đăng ký khóa học của một người dùng"""
        return list(cls.USER_COURSE_COLLECTION_NAME.find({"user_id": user_id}))

    @classmethod
    def delete_all_by_course_id(cls, course_id):
        """Xóa tất cả đăng ký liên quan đến một khóa học"""
        result = cls.USER_COURSE_COLLECTION_NAME.delete_many({"course_id": course_id})
        return result.deleted_count
