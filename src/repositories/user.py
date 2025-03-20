from src.models.user import UserModel
from src.util.formatters import pick_user
from src.validation.user import UserSchema
import bcrypt
import uuid

class UserRepository:
    @staticmethod
    def create_new(user_data):
        """Creates a new user after processing input data."""
        # Second-level validation (full schema validation)
        validated_data = UserSchema(**user_data).dict()

        # Check if email already exists
        if UserModel.find_by_email(user_data["email"]):
            raise ValueError("Email already exists!")

        # Hash password
        user_data["password"] = bcrypt.hashpw(
            user_data["password"].encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Create username from email
        user_data["username"] = user_data["email"].split("@")[0]
        user_data["verifyToken"] = str(uuid.uuid4())

       # Save user to database
        createdUserId = UserModel.create_new(user_data)
        get_new_user = UserModel.find_one_by_id(createdUserId)

        return pick_user(get_new_user)  # Return formatted user data

    @staticmethod
    def find_by_email(email):
        return UserModel.find_by_email(email)

    @staticmethod
    def find_one_by_id(user_id):
        return UserModel.find_one_by_id(user_id)
