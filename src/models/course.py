from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from bson import ObjectId

from src.config.mongodb import MongoDB

class CourseSchemaDB(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=5000)
    video_url: str = Field(...)
    video_duration: float = Field(default=0)
    video_format: str = Field(default="")
    video_public_id: str = Field(default="")
    thumbnail_url: str = Field(default="")
    thumbnail_public_id: str = Field(default="")
    user_id: str
    is_public: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v

    @field_validator('description')
    @classmethod
    def description_not_too_long(cls, v):
        if len(v) > 5000:
            raise ValueError('Description is too long (max 5000 characters)')
        return v

    @field_validator('video_url')
    @classmethod
    def video_url_must_be_valid(cls, v):
        if not v:
            raise ValueError('Video URL is required')
        return v

class CourseModel:
    COURSE_COLLECTION_NAME = MongoDB.get_db()["courses"]

    @classmethod
    def create_new(cls, course_data):
        validated_course = CourseSchemaDB(**course_data)
        course_dict = validated_course.model_dump()
        result = cls.COURSE_COLLECTION_NAME.insert_one(course_dict)
        return str(result.inserted_id)

    @classmethod
    def find_by_id(cls, course_id):
        if not ObjectId.is_valid(course_id):
            raise ValueError("Invalid course ID")
        course = cls.COURSE_COLLECTION_NAME.find_one({"_id": ObjectId(course_id)})
        if course:
            course["_id"] = str(course["_id"])
        return course

    @classmethod
    def update(cls, course_id, update_data):
        if not ObjectId.is_valid(course_id):
            raise ValueError("Invalid course ID")
        update_data["updated_at"] = datetime.utcnow()
        result = cls.COURSE_COLLECTION_NAME.find_one_and_update(
            {"_id": ObjectId(course_id)},
            {"$set": update_data},
            return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    @classmethod
    def delete(cls, course_id):
        if not ObjectId.is_valid(course_id):
            raise ValueError("Invalid course ID")
        result = cls.COURSE_COLLECTION_NAME.find_one_and_delete({"_id": ObjectId(course_id)})
        if result:
            result["_id"] = str(result["_id"])
        return result

    @classmethod
    def find_all(cls):
        courses = cls.COURSE_COLLECTION_NAME.find().sort("created_at", -1)
        return list(courses)

    @classmethod
    def find_public_courses(cls):
        courses = cls.COURSE_COLLECTION_NAME.find({"is_public": True}).sort("created_at", -1)
        return list(courses)
