from flask import Blueprint
from src.resources.user import UserResource

user_bp = Blueprint("user", __name__)

user_bp.route("/users/register", methods=["POST"])(UserResource.create_new)

user_bp.route("/users/verify", methods=["PUT"])(UserResource.verify_account)

user_bp.route("/users/login", methods=["POST"])(UserResource.login)