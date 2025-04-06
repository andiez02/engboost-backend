from flask import request, jsonify, make_response
from flask_cors.core import serialize_option

from src.repositories.user import UserRepository
from src.utils.api_error import ApiError
from src.utils.error_handlers import api_error_handler
from flask import g

from src.utils.formatters import pick_user
from src.utils.mongo_helper import serialize_mongo_data
from src.validation.user import (
    RegisterValidation,
    VerifyAccountValidation,
    LoginValidation,
    UpdateUserValidation,
    UpdateUserRoleValidation,
)

class UserResource:
    @staticmethod
    @api_error_handler
    def create_new():
        # Validate request body using Pydantic
        verified_data = RegisterValidation(**request.json)
        
        request_data = verified_data.model_dump()

        # Call repository to create user
        result = UserRepository.create_new(request_data)
        
        return jsonify({"message": "User registered successfully", "user": result}), 201

    @staticmethod
    @api_error_handler
    def verify_account():
        verified_data = VerifyAccountValidation(**request.json)

        request_data = verified_data.model_dump()

        result = UserRepository.verify_account(request_data)

        return jsonify({"message": "Account verified successfully", "user": result}), 200
    
    @staticmethod
    @api_error_handler
    def login():
        verified_data = LoginValidation(**request.json)

        request_data = verified_data.model_dump()

        result = UserRepository.login(request_data)

        # return http only cookie for browser

        response = make_response(jsonify({
            "message": "Account login successfully",
            "user": result
        }), 200)

        response.set_cookie(
            key="accessToken",
            value=result["accessToken"],
            httponly=True,
            secure=True,
            samesite="None",
            max_age=60 * 60 * 24 * 14 
        )

        response.set_cookie(
            key="refreshToken",
            value=result["refreshToken"],
            httponly=True,
            secure=True,
            samesite="None",
            max_age=60 * 60 * 24 * 14
        )

        return response

    @staticmethod
    @api_error_handler
    def logout():
        response = make_response(jsonify({"loggedOut": True}), 200)
        response.delete_cookie("accessToken", path="/", secure=True, samesite="None")
        response.delete_cookie("refreshToken", path="/", secure=True, samesite="None")
        return response

    @staticmethod
    @api_error_handler
    def refresh_token():
        refresh_token = request.cookies.get("refreshToken")
        if not refresh_token:
            raise ApiError(403, "Please Sign In! (Error from refresh Token)")

        result = UserRepository.refresh_token(refresh_token)

        response = make_response(jsonify(result), 200)
        response.set_cookie(
            key="accessToken",
            value=result["accessToken"],
            httponly=True,
            secure=True,
            samesite="None",
            max_age=60 * 60 * 24 * 14  
        )

        return response

    @staticmethod
    @api_error_handler
    async def update(user_avatar_file=None, **kwargs):
        # Get user_id from authenticated user
        user_id = g.user["_id"]
        
        # Handle form data for avatar upload
        if user_avatar_file:
            # Update user with avatar file
            result = UserRepository.update(user_id, {}, user_avatar_file)
            return jsonify({"message": "User avatar updated successfully", "user": result}), 200
        
        # Handle JSON data for other updates
        if not request.is_json:
            raise ApiError(415, "Content-Type must be application/json for non-file updates")
            
        # Validate update data
        verified_data = UpdateUserValidation(**request.json)
        update_data = verified_data.model_dump(exclude_none=True)
        
        # Update user
        result = UserRepository.update(user_id, update_data)
        return jsonify({"message": "User updated successfully", "user": result}), 200

    @staticmethod
    @api_error_handler
    def get_list_user():
        # Lấy tham số từ query string
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        search = request.args.get('search', '')

        # Tính toán offset
        offset = (page - 1) * limit

        # Gọi repository để lấy danh sách người dùng
        users, total_users = UserRepository.search_users(search, limit, offset)

        # Chuẩn bị response
        serialized_users = [serialize_mongo_data(user) for user in users]
        users_response = [pick_user(user) for user in serialized_users]

        return jsonify({
            "users": users_response,
            "pagination": {
                "total": total_users,
                "page": page,
                "limit": limit,
                "totalPages": (total_users + limit - 1) // limit
            }
        }), 200

    @staticmethod
    @api_error_handler
    def update_user_role(user_id):
        # Validate request body using Pydantic
        verified_data = UpdateUserRoleValidation(user_id=user_id, **request.json)

        # Extract data from the validated request
        request_data = verified_data.model_dump()
        new_role = request_data["role"]

        # Call the repository method to update the user's role
        result = UserRepository.update_user_role(user_id, new_role)

        return jsonify({"message": "User role updated successfully", "user": result}), 200

    @staticmethod
    @api_error_handler
    def delete_user(user_id):
        """
        Xóa người dùng và tất cả dữ liệu liên quan.

        Args:
            user_id: ID của người dùng cần xóa từ URL

        Returns:
            JSON response với thông báo xóa thành công
        """
        # Gọi repository để xóa người dùng và dữ liệu liên quan
        UserRepository.delete_user(user_id)

        return jsonify({
            "message": "User and all related data deleted successfully",
            "deleted": True
        }), 200
