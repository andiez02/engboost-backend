from flask import Blueprint
from routes.user import user_bp

api_bp = Blueprint("api", __name__)
api_bp.register_blueprint(user_bp, url_prefix="/api")
