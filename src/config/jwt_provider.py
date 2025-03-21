import jwt
from datetime import datetime, timedelta

class JwtProvider:
    @staticmethod
    def generate_token(user_info: dict, secret_signature: str, token_life: timedelta) -> str:
        try:
            expire_at = datetime.utcnow() + token_life
            payload = {**user_info, "exp": expire_at}
            return jwt.encode(payload, secret_signature, algorithm="HS256")
        except Exception as e:
            raise RuntimeError(f"Error generating token: {e}")

    @staticmethod
    def verify_token(token: str, secret_signature: str) -> dict:
        try:
            return jwt.decode(token, secret_signature, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
