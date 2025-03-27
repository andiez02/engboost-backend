from flask import Blueprint
from .user import user_bp
from .snaplang import snaplang_bp
from .course import course_bp

api_bp = Blueprint("api", __name__)

api_bp.register_blueprint(user_bp, url_prefix="/api/users")
api_bp.register_blueprint(snaplang_bp, url_prefix="/api/snaplang") 
api_bp.register_blueprint(course_bp, url_prefix="/api/courses")
