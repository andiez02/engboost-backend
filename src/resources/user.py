from flask import request, jsonify
from pydantic import BaseModel, EmailStr, constr, ValidationError, Field
from src.repositories.user import UserRepository
from src.exceptions import ApiError 
from src.utils.constants import (
    EMAIL_RULE,
    EMAIL_RULE_MESSAGE,
    PASSWORD_RULE,
    PASSWORD_RULE_MESSAGE,
)

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
    def create_new():
        try:
            # Validate request body using Pydantic
            verifiedData = RegisterValidation(**request.json)
           
            request_data = verifiedData.model_dump()

            # Call repository to create user
            result = UserRepository.create_new(request_data)
            
            return jsonify({"message": "User registered successfully", "user": result}), 201

        except ValidationError as e:
            raise ApiError(400, str(e))  
        except ValueError as e:
            raise ApiError(400, str(e)) 
        except ApiError as e:
            raise e 
        except Exception as e:
            print(f"Unexpected error: {e}")  
            raise ApiError(500, "Something went wrong!") 

    @staticmethod
    def verify_account():
        try:
            verifiedData = VerifyAccountValidation(**request.json)

            request_data = verifiedData.model_dump()

            result = UserRepository.verify_account(request_data)

            return jsonify({"message": "Account verified successfully", "user": result}), 200
        
        except ValidationError as e:
            raise ApiError(400, str(e))  
        except ValueError as e:
            raise ApiError(400, str(e)) 
        except ApiError as e:
            raise e 
        except Exception as e:
            print(f"Unexpected error: {e}") 
            raise ApiError(500, "Something went wrong!") 
        
    @staticmethod
    def login():
        try:
            verifiedData = LoginValidation(**request.json)

            request_data = verifiedData.model_dump()

            result = UserRepository.login(request_data)

            # return http only cookie for browser
            print(result)

            return jsonify({"message": "Account login successfully", "user": result}), 200
        
        except ValidationError as e:
            raise ApiError(400, str(e))  
        except ValueError as e:
            raise ApiError(400, str(e)) 
        except ApiError as e:
            raise e 
        except Exception as e:
            print(f"Unexpected error: {e}") 
            raise ApiError(500, "Something went wrong!") 

    @staticmethod
    def get_user_by_id(user_id):
        user = UserRepository.find_one_by_id(user_id)
        if not user:
            raise ApiError(404, "User not found") 

        # Convert ObjectId to string for JSON response
        user["_id"] = str(user["_id"])
        return jsonify(user), 200
