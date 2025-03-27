from flask import request
from src.repositories.course import CourseRepository
from src.exceptions import ApiError

class CourseResource:

    @staticmethod
    def get_all_courses():
        try:
            courses = CourseRepository.get_all_courses()
            return courses, 200
        except Exception as e:
            raise ApiError(500, f"Lỗi khi lấy danh sách khóa học: {str(e)}")

    @staticmethod
    def add_course():
        try:
            course_data = request.json
            course_id = CourseRepository.create_course(course_data)
            return {"message": "Thêm khóa học thành công", "id": course_id}, 201
        except Exception as e:
            raise ApiError(500, f"Lỗi khi thêm khóa học: {str(e)}")
