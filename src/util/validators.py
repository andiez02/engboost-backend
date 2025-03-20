from flask import request, jsonify
from functools import wraps

def validate_request(schema):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                data = schema(**request.json)  # Validate input
            except Exception as e:
                return jsonify({"error": str(e)}), 400
            
            request.validated_data = data  # Gán dữ liệu hợp lệ vào request
            return func(*args, **kwargs)
        return wrapper
    return decorator
