from flask import request, jsonify, make_response
from src.repositories.user import UserRepository
from src.utils.api_error import ApiError
from src.utils.error_handlers import api_error_handler
from flask import g
from src.validation.user import (
    RegisterValidation,
    VerifyAccountValidation,
    LoginValidation,
    UpdateUserValidation
)
from src.middleware.image_upload import image_upload_middleware

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
