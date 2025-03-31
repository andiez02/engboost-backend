from flask import request, g, jsonify
import jwt
from functools import wraps
import logging
from src.config.environment import ACCESS_TOKEN_SECRET, REFRESH_TOKEN_SECRET
from src.utils.api_error import ApiError
from src.config.jwt_provider import JwtProvider
from src.repositories.user import UserRepository

# Tạo logger
logger = logging.getLogger(__name__)

def is_authorized(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            logger.info("=== Authorization Check Started ===")
            
            # Lấy token từ cookie trong request
            access_token = request.cookies.get("accessToken")
            refresh_token = request.cookies.get("refreshToken")
            logger.info(f"Token from cookie: {'Found' if access_token else 'Not found'}")
            
            # Kiểm tra token trong header nếu không có trong cookie
            if not access_token:
                auth_header = request.headers.get("Authorization")
                logger.info(f"Authorization header: {auth_header}")
                if auth_header and auth_header.startswith("Bearer "):
                    access_token = auth_header.split(" ")[1]
                    logger.info("Token extracted from Authorization header")
            
            # Nếu không có token, báo lỗi 401 (Unauthorized)
            if not access_token:
                logger.warning("No token found in cookies or headers")
                raise ApiError(401, "Unauthorized! (Token not found)")

            # Giải mã token, kiểm tra tính hợp lệ
            try:
                decoded_token = jwt.decode(access_token, ACCESS_TOKEN_SECRET, algorithms=["HS256"])
                logger.info(f"Token decoded successfully: {decoded_token}")
            except jwt.ExpiredSignatureError:
                logger.warning("Access token expired")
                raise ApiError(410, "Access token expired. Please refresh token.")  # Trả về 410 để client biết cần refresh
            except jwt.InvalidTokenError as e:
                logger.warning(f"Invalid token: {str(e)}")
                raise ApiError(401, "Unauthorized! (Invalid token)")

            # Lưu thông tin user vào g để sử dụng trong request hiện tại
            g.user = decoded_token
            logger.info(f"User info stored in g.user: {g.user}")

            # Cho phép request tiếp tục đến route được bảo vệ
            logger.info("=== Authorization Check Completed ===")
            return f(*args, **kwargs)

        except ApiError as e:
            logger.error(f"API Error in auth middleware: {e.message} (Status: {e.status_code})")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in auth middleware: {str(e)}")
            raise ApiError(500, "Something went wrong!")

    return decorated_function
