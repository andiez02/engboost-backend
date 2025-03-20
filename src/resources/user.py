from flask import request, jsonify
from pydantic import BaseModel, EmailStr, constr, ValidationError
from src.repositories.user import UserRepository

class UserQuickValidation(BaseModel):
    email: EmailStr
    password: constr(min_length=6)
class UserResource:
    @staticmethod
    def create_new():
        try:
            # Validate request body using Pydantic
            data = UserQuickValidation(**request.json)
           
            request_data = data.model_dump()

            # Call repository to create user
            result = UserRepository.create_new(request_data)
            
            return jsonify({"message": "User registered successfully", "user": result}), 201

        except ValidationError as e:
            return jsonify({"error": e.errors()}), 400
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            print(f"Unexpected error: {e}")  # Log the error
        return jsonify({"error": "Something went wrong!"}), 500


    @staticmethod
    def get_user_by_id(user_id):
        user = UserRepository.find_one_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Convert ObjectId to string for JSON response
        user["_id"] = str(user["_id"])
        return jsonify(user), 200
