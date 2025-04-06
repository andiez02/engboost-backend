from src.models.course import CourseModel
from src.utils.api_error import ApiError
from src.utils.error_handlers import repo_error_handler
from src.utils.mongo_helper import serialize_mongo_data
from src.config.cloudinary import CloudinaryService
import logging
import cloudinary

class CourseRepository:
    @staticmethod
    @repo_error_handler
    def get_all_courses():
        courses = CourseModel.find_all()
        return [serialize_mongo_data(course) for course in courses]

    @staticmethod
    @repo_error_handler
    def upload_course_video(video_file):
        """Upload video khóa học lên Cloudinary và trả về thông tin video"""
        logger = logging.getLogger(__name__)
        logger.info("Uploading course video to Cloudinary")
        
        try:
            # Upload video lên Cloudinary
            video_data = CloudinaryService.upload_video(video_file, folder="courses")
            
            logger.info(f"Video uploaded successfully: {video_data['public_id']}")
            return video_data
        except Exception as e:
            logger.error(f"Error uploading course video: {str(e)}")
            raise ApiError(500, f"Failed to upload video: {str(e)}")

    @staticmethod
    @repo_error_handler
    def upload_course_thumbnail(thumbnail_file):
        """Upload thumbnail khóa học lên Cloudinary và trả về thông tin ảnh"""
        logger = logging.getLogger(__name__)
        logger.info("Uploading course thumbnail to Cloudinary")
        
        try:
            # Upload thumbnail lên Cloudinary
            result = cloudinary.uploader.upload(
                thumbnail_file,
                folder="course_thumbnails",
                resource_type="image"
            )
            
            logger.info(f"Thumbnail uploaded successfully: {result['public_id']}")
            return {
                "url": result["secure_url"],
                "public_id": result["public_id"]
            }
        except Exception as e:
            logger.error(f"Error uploading course thumbnail: {str(e)}")
            raise ApiError(500, f"Failed to upload thumbnail: {str(e)}")

    @staticmethod
    @repo_error_handler
    def create_course(course_data):
        course_id = CourseModel.create_new(course_data)
        return CourseModel.find_by_id(course_id)

    @staticmethod
    @repo_error_handler
    def get_course_by_id(course_id):
        course = CourseModel.find_by_id(course_id)
        if not course:
            raise ApiError(404, "Course not found")
        return serialize_mongo_data(course)

    @staticmethod
    @repo_error_handler
    def update_course(course_id, update_data):
        updated_course = CourseModel.update(course_id, update_data)
        if not updated_course:
            raise ApiError(404, "Course not found")
        return serialize_mongo_data(updated_course)

    @staticmethod
    @repo_error_handler
    def delete_course(course_id):
        logger = logging.getLogger(__name__)
        # Lấy thông tin course trước khi xóa
        course = CourseModel.find_by_id(course_id)
        if not course:
            raise ApiError(404, "Course not found")
        
        # Xóa video từ Cloudinary nếu có public_id
        if course.get("video_public_id"):
            logger.info(f"Deleting video from Cloudinary: {course['video_public_id']}")
            try:
                CloudinaryService.delete_video(course["video_public_id"])
            except Exception as e:
                logger.error(f"Error deleting video from Cloudinary: {str(e)}")
                # Tiếp tục xóa course ngay cả khi không xóa được video
        
        # Xóa thumbnail từ Cloudinary nếu có public_id
        if course.get("thumbnail_public_id"):
            logger.info(f"Deleting thumbnail from Cloudinary: {course['thumbnail_public_id']}")
            try:
                CloudinaryService.delete_image(course["thumbnail_public_id"])
            except Exception as e:
                logger.error(f"Error deleting thumbnail from Cloudinary: {str(e)}")
                # Tiếp tục xóa course ngay cả khi không xóa được thumbnail
        
        # Xóa course từ database
        deleted_course = CourseModel.delete(course_id)
        if not deleted_course:
            raise ApiError(404, "Course not found")
        return serialize_mongo_data(deleted_course)

    @staticmethod
    @repo_error_handler
    def get_public_courses():
        courses = CourseModel.find_public_courses()
        return [serialize_mongo_data(course) for course in courses]
