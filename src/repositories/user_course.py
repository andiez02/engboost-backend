from src.models.user_course import UserCourseModel
from src.models.course import CourseModel
from src.utils.api_error import ApiError
from src.utils.mongo_helper import serialize_mongo_data

class UserCourseRepository:
    @staticmethod
    def create_user_course(user_id, course_id):
        """Tạo đăng ký khóa học mới"""
        user_course_id = UserCourseModel.create_new(user_id, course_id)
        return {"user_course_id": user_course_id}

    @staticmethod
    def find_by_user_and_course(user_id, course_id):
        """Kiểm tra người dùng đã đăng ký khóa học chưa"""
        user_course = UserCourseModel.find_by_user_and_course(user_id, course_id)
        if user_course:
            return serialize_mongo_data(user_course)
        return None

    @staticmethod
    def get_courses_by_user(user_id):
        """Lấy danh sách khóa học đã đăng ký của người dùng"""
        user_courses = UserCourseModel.find_by_user(user_id)
        course_ids = [uc["course_id"] for uc in user_courses]

        # Lấy thông tin chi tiết của các khóa học
        courses = []
        for course_id in course_ids:
            course = CourseModel.find_by_id(course_id)
            if course:  # Chỉ thêm khóa học còn tồn tại
                courses.append(serialize_mongo_data(course))

        return courses
