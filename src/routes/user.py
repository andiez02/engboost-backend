from flask import Blueprint
from src.resources.user import UserResource
from src.middleware.auth_middleware import is_authorized 

user_bp = Blueprint("user", __name__)

user_bp.route("/register", methods=["POST"])(UserResource.create_new)
user_bp.route("/verify", methods=["PUT"])(UserResource.verify_account)
user_bp.route("/login", methods=["POST"])(UserResource.login)
user_bp.route("/logout", methods=["DELETE"])(UserResource.logout)
user_bp.route("/refresh_token", methods=["GET"])(UserResource.refresh_token)
user_bp.route("/get_user", methods=["GET"])(UserResource.get_user_by_id)
user_bp.route("/all", methods=["GET"])(UserResource.get_all_users)
user_bp.route("/<user_id>", methods=["DELETE"])(UserResource.delete_user)



