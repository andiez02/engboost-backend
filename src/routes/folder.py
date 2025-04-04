from flask import Blueprint
from src.resources.folder import FolderResource
from src.middleware.auth_middleware import is_authorized
from src.middleware.role_middleware import admin_required

folder_bp = Blueprint("folder", __name__)

# Folder routes
folder_bp.route("/folders", methods=["POST"])(is_authorized(FolderResource.create_folder))
folder_bp.route("/folders", methods=["GET"])(is_authorized(FolderResource.get_user_folders))
folder_bp.route("/folders/public", methods=["GET"])(is_authorized(FolderResource.get_public_folders))
folder_bp.route("/folders/<folder_id>", methods=["GET"])(is_authorized(FolderResource.get_folder))
folder_bp.route("/folders/<folder_id>", methods=["PUT"])(is_authorized(FolderResource.update_folder))
folder_bp.route("/folders/<folder_id>", methods=["DELETE"])(is_authorized(FolderResource.delete_folder))
folder_bp.route("/folders/<folder_id>/make-public", methods=["PUT"])(is_authorized(admin_required(FolderResource.make_folder_public)))

