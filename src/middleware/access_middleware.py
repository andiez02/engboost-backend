# src/middleware/course_access_middleware.py

from flask import jsonify, g
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def has_course_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info("=== Course Access Check Started ===")
        
        try:
            # Lấy user_id từ g.user (đã được set bởi is_authorized)
            user_id = g.user.get("_id")
            
            # Lấy course_id từ kwargs
            course_id = kwargs.get("course_id")
            
            if not course_id:
                logger.warning("No course_id provided in request")
                return jsonify({"success": False, "message": "Thiếu thông tin khóa học"}), 400
            
            # Admin có quyền truy cập tất cả khóa học
            from src.models.user import UserModel
            user = UserModel.find_by_id(user_id)
            
            if user and user.get("role") == "admin":
                logger.info(f"Admin access granted for user {user_id}")
                return f(*args, **kwargs)
            
            # Kiểm tra khóa học có công khai không
            from src.models.course import CourseModel
            course = CourseModel.find_by_id(course_id)
            
            if not course:
                logger.warning(f"Course {course_id} not found")
                return jsonify({"success": False, "message": "Khóa học không tồn tại"}), 404
            
            if course.get("is_public"):
                logger.info(f"Public course access granted for user {user_id}")
                return f(*args, **kwargs)
            
            # Kiểm tra người dùng đã đăng ký khóa học này chưa
            from src.models.user_course import UserCourseModel
            user_course = UserCourseModel.find_by_user_and_course(user_id, course_id)
            
            if not user_course:
                logger.warning(f"Access denied: User {user_id} has not registered for course {course_id}")
                return jsonify({
                    "success": False, 
                    "message": "Bạn cần đăng ký khóa học này để xem nội dung"
                }), 403
            
            logger.info(f"Registered user access granted for user {user_id}")
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error in course access middleware: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Có lỗi xảy ra khi kiểm tra quyền truy cập khóa học"
            }), 500
            
    return decorated_function
