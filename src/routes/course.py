from flask import Blueprint
from src.resources.user import CourseResource

course_bp = Blueprint("course", __name__)

course_bp.route("/users/register", methods=["GET"])(CourseResource.get_all_course)
