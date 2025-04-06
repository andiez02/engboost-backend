from flask import Blueprint, request, jsonify
from src.resources.course import CourseResource
from src.middleware.auth_middleware import is_authorized
from src.middleware.role_middleware import admin_required
from src.middleware.access_middleware import has_course_access
import logging

course_bp = Blueprint("course_bp", __name__)

# Kiểm tra upload file
@course_bp.route("/course-upload-test", methods=["POST"])
def test_upload():
    logger = logging.getLogger(__name__)
    logger.info("Test upload endpoint called")
    logger.info("Form data keys: %s", list(request.form.keys()))
    logger.info("Files keys: %s", list(request.files.keys()))

    response = {
        "form_data": {key: request.form[key] for key in request.form},
        "files": {key: request.files[key].filename for key in request.files}
    }

    return jsonify(response), 200

# Chỉ admin mới có quyền thêm, sửa, xóa khóa học
course_bp.route("/courses", methods=["POST"])(is_authorized(admin_required(CourseResource.create_course)))
course_bp.route("/courses/<course_id>", methods=["PUT"])(is_authorized(admin_required(CourseResource.update_course)))
course_bp.route("/courses/<course_id>", methods=["DELETE"])(is_authorized(admin_required(CourseResource.delete_course)))
course_bp.route("/courses/<course_id>", methods=["GET"])(is_authorized(admin_required(CourseResource.get_course)))

# Lấy danh sách khoá học (chỉ admin)
course_bp.route("/courses", methods=["GET"])(is_authorized(admin_required(CourseResource.get_all_courses)))

@course_bp.route("/public-courses", methods=["GET"])
def get_public_courses():
    return CourseResource.get_public_courses()

# Đăng ký khóa học
@course_bp.route("/courses/<course_id>/register", methods=["POST"])
@is_authorized
def register_course(course_id):
    return CourseResource.register_course(course_id)

# Lấy danh sách khóa học đã đăng ký của người dùng
@course_bp.route("/my-courses", methods=["GET"])
@is_authorized
def get_user_courses():
    return CourseResource.get_user_courses()

# Xem chi tiết khóa học đã đăng ký (người dùng phải đăng ký mới xem được)
@course_bp.route("/my-courses/<course_id>", methods=["GET"])
@is_authorized
def get_registered_course_detail(course_id):
    if has_course_access(lambda: True)(course_id):
        return CourseResource.get_course(course_id)
    else:
        return jsonify({"error": "Access denied"}), 403