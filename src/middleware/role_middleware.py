from functools import wraps
from flask import g
from src.utils.api_error import ApiError
from src.models.user import UserModel
import logging

logger = logging.getLogger(__name__)

def has_role(roles):
    """
    Middleware kiểm tra role của user
    :param roles: list các role được phép (['ADMIN', 'CLIENT'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Lấy user_id từ token
                user_id = g.user.get("_id")
                if not user_id:
                    raise ApiError(401, "Unauthorized! User ID not found in token")

                # Lấy thông tin user từ database
                user = UserModel.find_one_by_id(user_id)
                if not user:
                    raise ApiError(404, "User not found")

                # Lấy role từ database
                user_role = user.get("role", "CLIENT") 
                
                if user_role not in roles:
                    logger.warning(f"User {user.get('email')} with role {user_role} attempted to access endpoint requiring roles {roles}")
                    raise ApiError(403, f"Access denied. Required roles: {', '.join(roles)}")
                
                logger.info(f"User {user.get('email')} with role {user_role} accessed endpoint")
                return f(*args, **kwargs)
                
            except ApiError as e:
                logger.error(f"Role check failed: {e.message}")
                raise e
            except Exception as e:
                logger.error(f"Unexpected error in role middleware: {str(e)}")
                raise ApiError(500, "Something went wrong!")

        return decorated_function
    return decorator

# Các decorator tiện ích
def admin_required(f):
    """Decorator cho các endpoint yêu cầu quyền admin"""
    return has_role(['ADMIN'])(f)

def client_required(f):
    """Decorator cho các endpoint yêu cầu quyền client"""
    return has_role(['CLIENT'])(f)

def admin_or_client(f):
    """Decorator cho các endpoint cho phép cả admin và client"""
    return has_role(['ADMIN', 'CLIENT'])(f) 