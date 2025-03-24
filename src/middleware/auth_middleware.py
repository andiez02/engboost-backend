from flask import request, jsonify
import jwt
from functools import wraps
from src.config.environment import ACCESS_TOKEN_SECRET
from src.exceptions import ApiError

def is_authorized(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Lấy token từ cookie trong request
            access_token = request.cookies.get("accessToken")

            # Nếu không có token, báo lỗi 401 (Unauthorized)
            if not access_token:
                raise ApiError(401, "Unauthorized! (Token not found)")

            # Giải mã token, kiểm tra tính hợp lệ
            try:
                decoded_token = jwt.decode(access_token, ACCESS_TOKEN_SECRET, algorithms=["HS256"])
                print("Decoded token: ", decoded_token)
            except jwt.ExpiredSignatureError:
                raise ApiError(410, "Need to refresh token.")  # Token hết hạn
            except jwt.InvalidTokenError:
                raise ApiError(401, "Unauthorized! (Invalid token)")  # Token không hợp lệ

            # Lưu thông tin user vào request để sử dụng sau này
            request.jwt_decoded = decoded_token

            # Cho phép request tiếp tục đến route được bảo vệ
            return f(*args, **kwargs)

        except ApiError as e:
            return jsonify({"error": str(e)}), e.status_code

        except Exception as e:
            print(f"Unexpected error in auth middleware: {e}")  
            return jsonify({"error": "Something went wrong!"}), 500

    return decorated_function
