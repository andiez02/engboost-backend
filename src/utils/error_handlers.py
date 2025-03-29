from functools import wraps
from pydantic import ValidationError
from src.utils.api_error import ApiError
import logging
from bson.errors import InvalidId

def api_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            print(f"Validation error: {str(e)}")
            raise ApiError(400, str(e))
        except ValueError as e:
            print(f"Value error: {str(e)}")
            raise ApiError(400, str(e))
        except ApiError as e:
            print(f"API error: {e.message}")
            raise e
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise ApiError(500, "Something went wrong!")
    return wrapper

def repo_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(f"Value error in repository: {str(e)}")
            raise ApiError(400, str(e))
        except ApiError as e:
            print(f"API error in repository: {e.message}")
            raise e
        except Exception as e:
            print(f"Unexpected error in repository: {str(e)}")
            error_message = f"An error occurred while {func.__name__.replace('_', ' ')}"
            raise ApiError(500, error_message)
    return wrapper

def model_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            print(f"Validation error in model: {str(e)}")
            raise ApiError(400, str(e))
        except InvalidId as e:
            print(f"Invalid MongoDB ID: {str(e)}")
            raise ApiError(400, "Invalid ID format")
        except ApiError as e:
            # Truyền tiếp ApiError đã được tạo
            print(f"API error in model: {e.message}")
            raise e
        except Exception as e:
            operation = func.__name__.replace('_', ' ')
            collection = args[0].__name__ if args and hasattr(args[0], '__name__') else "data"
            print(f"Unexpected error in model ({operation}): {str(e)}")
            raise ApiError(500, f"Database error while {operation} {collection}")
    return wrapper