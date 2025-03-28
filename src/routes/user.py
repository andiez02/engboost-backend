from flask import Blueprint
from src.resources.user import UserResource
from src.middleware.auth_middleware import is_authorized 

user_bp = Blueprint("user", __name__)

user_bp.route("/register", methods=["POST"])(UserResource.create_new)
user_bp.route("/verify", methods=["PUT"])(UserResource.verify_account)
user_bp.route("/login", methods=["POST"])(UserResource.login)
user_bp.route("/logout", methods=["DELETE"])(UserResource.logout)
user_bp.route("/refresh_token", methods=["GET"])(UserResource.refresh_token)



