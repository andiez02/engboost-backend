from flask import request, jsonify, g
from src.repositories.course import CourseRepository
from src.repositories.user_course import UserCourseRepository
from src.models.user_course import UserCourseModel
from src.utils.api_error import ApiError
from src.utils.error_handlers import api_error_handler
from src.config.cloudinary import CloudinaryService
from src.utils.file_validator import FileValidator
from src.validation.course import validate_course_creation, validate_course_update
import logging

class CourseResource:
    @staticmethod
    @api_error_handler
    def get_all_courses():
        # Có thể thêm logic để lọc khóa học theo các tiêu chí khác nhau
        courses = CourseRepository.get_all_courses()
        return jsonify({"courses": courses}), 200

    @staticmethod
    @api_error_handler
    def create_course():
        logger = logging.getLogger(__name__)
        
        # Debug request
        logger.info("Request form data keys: %s", list(request.form.keys()))
        logger.info("Request files keys: %s", list(request.files.keys()))
        
        # Validate dữ liệu từ form
        validate_course_creation(request.form)
        
        # Nhận dữ liệu từ form
        course_title = request.form.get("title")
        course_description = request.form.get("description", "")
        is_public = request.form.get("is_public", "false").lower() == "true"
        
        video_file = request.files["video"]
        thumbnail_file = request.files["thumbnail"]
        
        # Kiểm tra định dạng và kích thước file video
        FileValidator.validate_video(video_file)
        
        # Kiểm tra định dạng và kích thước file thumbnail
        FileValidator.validate_image(thumbnail_file)
        
        # Upload video lên Cloudinary
        logger.info(f"Uploading video for course: {course_title}")
        video_data = CourseRepository.upload_course_video(video_file)
        
        # Upload thumbnail lên Cloudinary
        logger.info(f"Uploading thumbnail for course: {course_title}")
        thumbnail_data = CourseRepository.upload_course_thumbnail(thumbnail_file)
        
        # Khởi tạo dữ liệu khóa học
        course_data = {
            "title": course_title,
            "description": course_description,
            "video_url": video_data["url"],
            "user_id": g.user["_id"],
            "is_public": is_public,
            "video_duration": video_data.get("duration", 0),
            "video_format": video_data.get("format", ""),
            "video_public_id": video_data.get("public_id", ""),
            "thumbnail_url": thumbnail_data["url"],
            "thumbnail_public_id": thumbnail_data["public_id"]
        }
        
        # Tạo khóa học trong database
        result = CourseRepository.create_course(course_data)
        return jsonify({"message": "Course created successfully", "course": result}), 201

    @staticmethod
    @api_error_handler
    def get_course(course_id):
        result = CourseRepository.get_course_by_id(course_id)
        return jsonify(result), 200


    @staticmethod
    @api_error_handler
    def update_course(course_id):
        logger = logging.getLogger(__name__)
        
        # Validate dữ liệu cập nhật từ form
        validate_course_update(request.form)
        
        # Lấy thông tin course hiện tại
        current_course = CourseRepository.get_course_by_id(course_id)
        
        # Nhận dữ liệu từ form
        update_data = {}
        
        # Cập nhật thông tin cơ bản
        if "title" in request.form:
            update_data["title"] = request.form.get("title")
        
        if "description" in request.form:
            update_data["description"] = request.form.get("description")
        
        if "is_public" in request.form:
            update_data["is_public"] = request.form.get("is_public").lower() == "true"
        
        # Kiểm tra xem có file video mới không
        if "video" in request.files and request.files["video"].filename:
            video_file = request.files["video"]
            
            # Kiểm tra định dạng và kích thước file video
            FileValidator.validate_video(video_file)
            
            # Upload video mới lên Cloudinary
            logger.info(f"Uploading new video for course: {course_id}")
            video_data = CourseRepository.upload_course_video(video_file)
            
            # Cập nhật thông tin video
            update_data["video_url"] = video_data["url"]
            update_data["video_duration"] = video_data.get("duration", 0)
            update_data["video_format"] = video_data.get("format", "")
            update_data["video_public_id"] = video_data.get("public_id", "")
            
            # Xóa video cũ trên Cloudinary nếu có
            if current_course.get("video_public_id"):
                try:
                    logger.info(f"Deleting old video: {current_course['video_public_id']}")
                    CloudinaryService.delete_video(current_course["video_public_id"])
                except Exception as e:
                    logger.error(f"Error deleting old video: {str(e)}")

            # Nếu khóa học chuyển sang chế độ riêng tư → xóa các đăng ký liên quan
            if "is_public" in update_data and update_data["is_public"] is False:
                logger.info(f"Removing user registrations for private course: {course_id}")
                deleted_count = UserCourseModel.delete_all_by_course_id(course_id)
                logger.info(f"Deleted {deleted_count} user_course registrations")
        
        # Kiểm tra xem có file thumbnail mới không
        if "thumbnail" in request.files and request.files["thumbnail"].filename:
            thumbnail_file = request.files["thumbnail"]
            
            # Kiểm tra định dạng và kích thước file thumbnail
            FileValidator.validate_image(thumbnail_file)
            
            # Upload thumbnail mới lên Cloudinary
            logger.info(f"Uploading new thumbnail for course: {course_id}")
            thumbnail_data = CourseRepository.upload_course_thumbnail(thumbnail_file)
            
            # Cập nhật thông tin thumbnail
            update_data["thumbnail_url"] = thumbnail_data["url"]
            update_data["thumbnail_public_id"] = thumbnail_data["public_id"]
            
            # Xóa thumbnail cũ trên Cloudinary nếu có
            if current_course.get("thumbnail_publica_id"):
                try:
                    logger.info(f"Deleting old thumbnail: {current_course['thumbnail_public_id']}")
                    CloudinaryService.delete_image(current_course["thumbnail_public_id"])
                except Exception as e:
                    logger.error(f"Error deleting old thumbnail: {str(e)}")
        
        # Cập nhật course trong database
        result = CourseRepository.update_course(course_id, update_data)
        return jsonify({"message": "Course updated successfully", "course": result}), 200

    @staticmethod
    @api_error_handler
    def delete_course(course_id):
        result = CourseRepository.delete_course(course_id)
        return jsonify({"message": "Course deleted successfully", "course": result}), 200

    @staticmethod
    @api_error_handler
    def get_public_courses():
        courses = CourseRepository.get_public_courses()
        return jsonify({"courses": courses}), 200

    @staticmethod
    @api_error_handler
    def register_course(course_id):
        """Đăng ký khóa học cho người dùng"""
        user_id = g.user["_id"]
        # Kiểm tra khóa học tồn tại
        course = CourseRepository.get_course_by_id(course_id)
        if not course:
            raise ApiError(404, "Khóa học không tồn tại")

        # Kiểm tra người dùng đã đăng ký chưa
        existing = UserCourseRepository.find_by_user_and_course(user_id, course_id)
        if existing:
            raise ApiError(400, "Bạn đã đăng ký khóa học này rồi")

        # Tạo đăng ký mới
        result = UserCourseRepository.create_user_course(user_id, course_id)

        return jsonify({
            "success": True,
            "message": "Đăng ký khóa học thành công",
            "data": result
        }), 201

    @staticmethod
    @api_error_handler
    def get_user_courses():
        user_id = g.user["_id"]
        """Lấy danh sách khóa học đã đăng ký của người dùng"""
        user_courses = UserCourseRepository.get_courses_by_user(user_id)

        # Lọc chỉ lấy các khóa học công khai
        public_courses = [course for course in user_courses if course.get("is_public")]

        return jsonify({
            "success": True,
            "courses": public_courses
        }), 200
