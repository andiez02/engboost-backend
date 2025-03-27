from flask import request, jsonify, make_response
from pydantic import BaseModel, EmailStr, constr, ValidationError, Field
from src.repositories.user import UserRepository
from src.utils.api_error import ApiError
from src.utils.constants import (
    EMAIL_RULE,
    EMAIL_RULE_MESSAGE,
    PASSWORD_RULE,
    PASSWORD_RULE_MESSAGE,
)
from src.utils.error_handlers import api_error_handler

class RegisterValidation(BaseModel):
    email: EmailStr = Field(..., pattern=EMAIL_RULE.pattern, description=EMAIL_RULE_MESSAGE)  
    password: str = Field(..., min_length=8, description=PASSWORD_RULE_MESSAGE)

class VerifyAccountValidation(BaseModel):
    email: EmailStr = Field(..., pattern=EMAIL_RULE.pattern, description=EMAIL_RULE_MESSAGE)  
    token: str = Field(...,)

class LoginValidation(BaseModel):
    email: EmailStr = Field(..., pattern=EMAIL_RULE.pattern, description=EMAIL_RULE_MESSAGE)  
    password: str = Field(..., min_length=8, description=PASSWORD_RULE_MESSAGE)


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
        print(result)

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
            max_age=60 * 60 * 24 * 14  # 14 ngày
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
    def get_user_by_id(user_id):
        user = UserRepository.find_one_by_id(user_id)
        if not user:
            raise ApiError(404, "User not found") 

        # Convert ObjectId to string for JSON response
        user["_id"] = str(user["_id"])
        return jsonify(user), 200
