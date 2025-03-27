from flask import Blueprint
from src.resources.course import CourseResource

course_bp = Blueprint("course", __name__)

course_bp.route("/all", methods=["GET"])(CourseResource.get_all_courses)
course_bp.route("/", methods=["POST"])(CourseResource.add_course)
