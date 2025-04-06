from src.models.user import UserModel
from src.utils.formatters import pick_user
from src.utils.mongo_helper import serialize_mongo_data
from src.utils.api_error import ApiError
from src.validation.user import UserSchema
from src.config.environment import WEBSITE_DOMAIN, ACCESS_TOKEN_SECRET, ACCESS_TOKEN_LIFE, REFRESH_TOKEN_SECRET, REFRESH_TOKEN_LIFE
from src.config.jwt_provider import JwtProvider
from src.utils.error_handlers import repo_error_handler
from src.utils.email_helper import send_email_async
import bcrypt
import uuid
from src.config.cloudinary import CloudinaryService
from src.config.mongodb import MongoDB

class UserRepository:
    @staticmethod
    @repo_error_handler
    def create_new(reqData):
        """Creates a new user after processing input data."""
        print("🚀 ~ request data:", reqData)  # In ra dữ liệu yêu cầu

        # Kiểm tra nếu email đã tồn tại
        if UserModel.find_one_by_email(reqData.get("email")):
            raise ValueError("Email already exists!")

        # Hash password
        reqData["password"] = bcrypt.hashpw(
            reqData["password"].encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Tạo username từ email
        reqData["username"] = reqData["email"].split("@")[0]
        reqData["verifyToken"] = str(uuid.uuid4())

        # Lưu người dùng vào cơ sở dữ liệu
        createdUserId = UserModel.create_new(reqData)
        get_new_user = UserModel.find_one_by_id(createdUserId)

        # Gửi email xác thực
        verification_link = f"{WEBSITE_DOMAIN}/account/verification?email={get_new_user['email']}&token={get_new_user['verifyToken']}"
        custom_subject = "Please Verify Your Email Address"
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Verification</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Welcome to Our Service!</h2>
                <p>Hi there,</p>
                <p>Thanks for signing up! Please verify your email address by clicking the link below:</p>
                <p style="text-align: center;">
                    <a href="{verification_link}" style="display: inline-block; padding: 10px 20px; background-color: #3498db; color: #ffffff; text-decoration: none; border-radius: 5px;">Verify Your Email</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #2980b9;">{verification_link}</p>
                <p>If you didn't create an account, feel free to ignore this email.</p>
                <p>We're excited to have you on board!</p>
                <p>Sincerely,<br>Andiez<br>Team</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #777;">This is an automated email, please do not reply directly.</p>
            </div>
        </body>
        </html>
        """
        send_email_async(get_new_user["email"], custom_subject, html_content)

        return pick_user(get_new_user)  

    @staticmethod
    @repo_error_handler
    def verify_account(reqData):
        exist_user = UserModel.find_one_by_email(reqData.get("email"));
    
        # Kiểm tra nếu user không tồn tại
        if not exist_user:
            raise ApiError(404, "User not found!") 
        
        # Kiểm tra nếu tài khoản đã được kích hoạt
        if exist_user.get("isActive", False):
            raise ApiError(406, "Your account is already active")
        
        # Kiểm tra token có hợp lệ hay không
        if reqData["token"] != exist_user.get("verifyToken"):
            raise ApiError(406, "Token is invalid")
        
        update_data = {
            "isActive": True,
            "verifyToken": None
        }

        updated_user = UserModel.update(exist_user["_id"], update_data)

        return pick_user(updated_user)
    
    @staticmethod
    @repo_error_handler
    def login(reqData):
        exist_user = UserModel.find_one_by_email(reqData.get("email"))

        # Kiểm tra nếu user không tồn tại
        if not exist_user:
            raise ApiError(404, "User not found!") 
        
        # Kiểm tra nếu tài khoản đã được kích hoạt
        if not exist_user.get("isActive", False):
            raise ApiError(406, "Your account is not active")

        # Kiểm tra mật khẩu
        if not bcrypt.checkpw(reqData["password"].encode("utf-8"), exist_user["password"].encode("utf-8")):
            raise ApiError(406, "Your Email or Password is incorrect")
    
        # Tạo thông tin để đính kèm trong JWT Token
        user_info = {
            "_id": str(exist_user["_id"]),
            "email": exist_user["email"]
        }
        
        # Tạo Access Token và Refresh Token
        access_token = JwtProvider.generate_token(
            user_info,
            ACCESS_TOKEN_SECRET,
            ACCESS_TOKEN_LIFE
        )
        
        refresh_token = JwtProvider.generate_token(
            user_info,
            REFRESH_TOKEN_SECRET,
            REFRESH_TOKEN_LIFE
        )

        user = serialize_mongo_data(exist_user)
        user["accessToken"] = access_token
        user["refreshToken"] = refresh_token
        
        # Trả về thông tin người dùng kèm token
        return user

    @staticmethod
    @repo_error_handler
    def refresh_token(client_refresh_token):
        # Giải mã refreshToken để kiểm tra tính hợp lệ
        refresh_token_decoded = JwtProvider.verify_token(
            client_refresh_token, REFRESH_TOKEN_SECRET
        )

        user_info = {
            "_id": refresh_token_decoded["_id"],
            "email": refresh_token_decoded["email"]
        }

        # Tạo accessToken mới
        access_token = JwtProvider.generate_token(
            user_info,
            ACCESS_TOKEN_SECRET,
            ACCESS_TOKEN_LIFE  # Thời gian sống của accessToken
        )

        return {"accessToken": access_token}

    # @staticmethod
    # @repo_error_handler
    # def find_by_email(email):
    #     return UserModel.find_by_email(email)

    @staticmethod
    @repo_error_handler
    def find_one_by_id(user_id):
        return UserModel.find_one_by_id(user_id)

    @staticmethod
    @repo_error_handler
    def update(user_id, update_data, user_avatar_file=None):
        exist_user = UserModel.find_one_by_id(user_id)
        if not exist_user:
            raise ApiError(404, "Account not found!")

        if not exist_user.get("isActive", False):
            raise ApiError(406, "Your account is not active")
        
        updated_user = {}

        # Change Password
        if update_data.get("current_password") and update_data.get("new_password"):
            if not bcrypt.checkpw(update_data["current_password"].encode("utf-8"), exist_user["password"].encode("utf-8")):
                raise ApiError(406, "Your current password is incorrect")
            
            update_user = UserModel.update(user_id, {
                "password": bcrypt.hashpw(update_data["new_password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            })

        # Handle avatar update
        elif user_avatar_file:
            # Upload avatar to cloud storage and get URL
            avatar_result = CloudinaryService.upload_image(user_avatar_file, folder="avatars")
            update_data["avatar"] = avatar_result["url"]
            update_data["avatar_public_id"] = avatar_result["public_id"]
            updated_user = UserModel.update(user_id, update_data)

        # Update other information
        else: 
            updated_user = UserModel.update(user_id, update_data)
            
        return pick_user(updated_user)

    @staticmethod
    @repo_error_handler
    def get_all_users():
        try:
            # Fetch all users from the database
            users_cursor = UserModel.USER_COLLECTION_NAME.find({})
            users = list(users_cursor)
            return users
        except Exception as e:
            raise ApiError(500, "An error occurred while fetching users.")

    @staticmethod
    @repo_error_handler
    def get_users_paginated(limit, offset):
        try:
            # Lấy danh sách người dùng với phân trang
            users_cursor = UserModel.USER_COLLECTION_NAME.find({}).skip(offset).limit(limit)
            users = list(users_cursor)
            return users
        except Exception as e:
            raise ApiError(500, "An error occurred while fetching users.")

    @staticmethod
    @repo_error_handler
    def count_users():
        try:
            # Đếm tổng số người dùng
            return UserModel.USER_COLLECTION_NAME.count_documents({})
        except Exception as e:
            raise ApiError(500, "An error occurred while counting users.")

    @staticmethod
    @repo_error_handler
    def update_user_role(user_id, new_role):
        # Fetch the existing user
        user = UserModel.find_one_by_id(user_id)
        if not user:
            raise ApiError(404, "User not found!")

        # Prevent updates to the specific account
        if user.get("email") == "admin@yopmail.com":
            raise ApiError(403, "This account cannot be updated.")

        # Update the user's role
        updated_user = UserModel.update(user_id, {"role": new_role})

        return pick_user(updated_user)

    @staticmethod
    @repo_error_handler
    def delete_user(user_id):
        """
        Xóa người dùng và tất cả dữ liệu liên quan.

        Args:
            user_id: ID của người dùng cần xóa

        Returns:
            bool: True nếu xóa thành công

        Raises:
            ApiError: Nếu có lỗi xảy ra trong quá trình xóa
        """
        from bson import ObjectId
        from src.models.folder import FolderModel
        from src.models.flashcard import FlashcardModel
        from src.config.cloudinary import CloudinaryService

        # Kiểm tra người dùng có tồn tại không
        user = UserModel.find_one_by_id(user_id)
        if not user:
            raise ApiError(404, "User not found!")

        # Ngăn chặn xóa tài khoản admin@yopmail.com
        if user.get("email") == "admin@yopmail.com":
            raise ApiError(403, "This account cannot be deleted.")

        # Ngăn chặn xóa tài khoản có vai trò ADMIN
        if user.get("role") == "ADMIN":
            raise ApiError(403, "Admin accounts cannot be deleted. Change the role to CLIENT first.")

        # Chuyển đổi user_id thành ObjectId nếu cần
        if isinstance(user_id, str):
            user_id_obj = ObjectId(user_id)
        else:
            user_id_obj = user_id

        # Lấy client từ MongoDB
        client = MongoDB.client

        # Lưu trữ public_ids của hình ảnh cần xóa từ Cloudinary
        images_to_delete = []

        # Thêm avatar người dùng nếu có
        if user.get("avatar_public_id"):
            images_to_delete.append(user["avatar_public_id"])

        # Bắt đầu transaction
        with client.start_session() as session:
            try:
                # Bắt đầu transaction
                session.start_transaction()

                # 1. Lấy tất cả folder của người dùng
                user_folders = list(FolderModel.FOLDER_COLLECTION_NAME.find(
                    {"userId": user_id_obj},
                    session=session
                ))

                # 2. Xử lý từng folder
                for folder in user_folders:
                    folder_id = folder["_id"]

                    # Lấy tất cả flashcard trong folder
                    flashcards = list(FlashcardModel.FLASHCARD_COLLECTION_NAME.find(
                        {"folderId": folder_id},
                        session=session
                    ))

                    # Thu thập public_ids của hình ảnh flashcard
                    for flashcard in flashcards:
                        if flashcard.get("image_public_id"):
                            images_to_delete.append(flashcard["image_public_id"])

                    # Xóa tất cả flashcard trong folder
                    FlashcardModel.FLASHCARD_COLLECTION_NAME.delete_many(
                        {"folderId": folder_id},
                        session=session
                    )

                # 3. Xóa tất cả folder của người dùng
                FolderModel.FOLDER_COLLECTION_NAME.delete_many(
                    {"userId": user_id_obj},
                    session=session
                )

                # 4. Xóa người dùng
                result = UserModel.USER_COLLECTION_NAME.delete_one(
                    {"_id": user_id_obj},
                    session=session
                )

                if result.deleted_count == 0:
                    # Nếu không xóa được người dùng, hủy bỏ transaction
                    session.abort_transaction()
                    raise ApiError(500, "Failed to delete user.")

                # Commit transaction nếu tất cả thao tác thành công
                session.commit_transaction()

            except Exception as e:
                # Nếu có lỗi, hủy bỏ transaction
                if session.in_transaction:
                    session.abort_transaction()
                raise ApiError(500, f"Error during user deletion: {str(e)}")

        # Sau khi transaction thành công, xóa hình ảnh từ Cloudinary
        # (Thực hiện bên ngoài transaction vì đây là dịch vụ bên ngoài)
        for image_id in images_to_delete:
            try:
                CloudinaryService.delete_image(image_id)
            except Exception as e:
                # Log lỗi nhưng không làm gián đoạn quá trình
                print(f"Warning: Failed to delete image {image_id} from Cloudinary: {e}")

        return True

    @staticmethod
    @repo_error_handler
    def search_users(search_query, limit=10, offset=0):
        """
        Tìm kiếm người dùng theo username, email hoặc fullName
        """
        query = {}

        # Thêm điều kiện tìm kiếm nếu có
        if search_query:
            query["$or"] = [
                {"username": {"$regex": search_query, "$options": "i"}},
                {"email": {"$regex": search_query, "$options": "i"}},
                {"fullName": {"$regex": search_query, "$options": "i"}}
            ]

        # Đếm tổng số kết quả
        total_count = UserModel.USER_COLLECTION_NAME.count_documents(query)

        # Lấy danh sách người dùng với phân trang
        users = list(UserModel.USER_COLLECTION_NAME.find(query).sort("createdAt", -1).skip(offset).limit(limit))

        return users, total_count




