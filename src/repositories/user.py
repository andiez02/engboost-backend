from src.models.user import UserModel
from src.utils.formatters import pick_user
from src.utils.mongo_helper import serialize_mongo_data
from src.validation.user import UserSchema
from src.config.brevo import send_email
from src.config.environment import WEBSITE_DOMAIN, ACCESS_TOKEN_SECRET, ACCESS_TOKEN_LIFE, REFRESH_TOKEN_SECRET, REFRESH_TOKEN_LIFE
from src.exceptions import ApiError 
from src.config.jwt_provider import JwtProvider
import bcrypt
import uuid

class UserRepository:
    @staticmethod
    def create_new(reqData):
        try:
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
                    <p>If you didn’t create an account, feel free to ignore this email.</p>
                    <p>We’re excited to have you on board!</p>
                    <p>Sincerely,<br>Andiez<br>Team</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="font-size: 12px; color: #777;">This is an automated email, please do not reply directly.</p>
                </div>
            </body>
            </html>
            """
            send_email(get_new_user["email"], custom_subject, html_content)

            return pick_user(get_new_user)  # Return formatted user data

        except ValueError as e:
            raise ApiError(400, str(e))  # Raise ApiError for validation errors
        except Exception as e:
            print(f"Error creating user: {e}")  # Log the error for debugging
            raise ApiError(500, "An error occurred while creating the user.")  # Handle unexpected errors

    @staticmethod
    def verify_account(reqData):
        try:
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
        
        except ApiError as e:
            raise e 
        except Exception as e:
            print("An error occurred while verifying the account:", e)
            raise ApiError(500, "An error occurred while verifying the account.") 
    
    @staticmethod
    def login(reqData):
        try:
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
            
            # Trả về thông tin người dùng kèm token
            return {
                "accessToken": access_token,
                "refreshToken": refresh_token,
                "user": serialize_mongo_data(exist_user)
            }
        except ApiError as e:
            raise e 
        except Exception as e:
            print(f"Unexpected error during login: {e}")  # Log the error for debugging
            raise ApiError(500, "An unexpected error occurred during login.")  # Provide a more specific error me
    
    @staticmethod
    def find_by_email(email):
        try:
            return UserModel.find_by_email(email)
        except Exception as e:
            raise ApiError(500, "An error occurred while finding the user by email.") 

    @staticmethod
    def find_one_by_id(user_id):
        try:
            return UserModel.find_one_by_id(user_id)
        except Exception as e:
            raise ApiError(500, "An error occurred while finding the user by ID.")  # Handle unexpected errors
