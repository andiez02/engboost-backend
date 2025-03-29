from flask import Blueprint
<<<<<<< HEAD
from src.resources.course import CourseResource

course_bp = Blueprint("course", __name__)

course_bp.route("/all", methods=["GET"])(CourseResource.get_all_courses)
course_bp.route("/", methods=["POST"])(CourseResource.add_course)
=======
from src.resources.user import CourseResource

course_bp = Blueprint("course", __name__)

course_bp.route("/users/register", methods=["GET"])(CourseResource.get_all_course)
>>>>>>> d735b66f97253061afaf269aaef92728b9636b13
