from flask import Blueprint, request
from src.resources.user import UserResource
from src.middleware.auth_middleware import is_authorized
from src.middleware.image_upload import image_upload_middleware
from asgiref.sync import async_to_sync

user_bp = Blueprint("user", __name__)

user_bp.route("/register", methods=["POST"])(UserResource.create_new)
user_bp.route("/verify", methods=["PUT"])(UserResource.verify_account)
user_bp.route("/login", methods=["POST"])(UserResource.login)
user_bp.route("/logout", methods=["DELETE"])(UserResource.logout)
user_bp.route("/refresh_token", methods=["GET"])(UserResource.refresh_token)

# Route xử lý cập nhật thông tin user
@user_bp.route("/update", methods=["PUT"])
@is_authorized  # Middleware kiểm tra xác thực người dùng
def update_route():
    # Kiểm tra xem request có chứa file avatar không
    if "avatar" in request.files:
        # Nếu có file avatar:
        # 1. Lấy hàm upload từ middleware (image_upload_middleware["upload"])
        # 2. Cấu hình để chỉ chấp nhận 1 file với tên field là "avatar" (.single("avatar"))
        # 3. Truyền hàm UserResource.update vào middleware để xử lý sau khi validate file
        # 4. Chuyển đổi hàm async thành sync vì Flask không hỗ trợ async trực tiếp
        return async_to_sync(image_upload_middleware["upload"].single("avatar")(UserResource.update))()
    else:
        # Nếu không có file avatar:
        # 1. Gọi trực tiếp hàm update để xử lý cập nhật thông tin thông thường
        # 2. Chuyển đổi hàm async thành sync
        return async_to_sync(UserResource.update)()

