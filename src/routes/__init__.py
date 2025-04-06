from flask import Blueprint
from .user import user_bp
from .snaplang import snaplang_bp
from src.routes.folder import folder_bp
from src.routes.flashcard import flashcard_bp
from src.routes.course import course_bp
api_bp = Blueprint("api", __name__)

api_bp.register_blueprint(user_bp, url_prefix="/api/users")
api_bp.register_blueprint(snaplang_bp, url_prefix="/api/snaplang") 
api_bp.register_blueprint(folder_bp, url_prefix="/api")
api_bp.register_blueprint(flashcard_bp, url_prefix="/api")
api_bp.register_blueprint(course_bp, url_prefix="/api")