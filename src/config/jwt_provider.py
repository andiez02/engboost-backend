import jwt
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class JwtProvider:
    @staticmethod
    def generate_token(user_info: dict, secret_signature: str, token_life: timedelta) -> str:
        try:
            # Sử dụng UTC time để tránh vấn đề múi giờ
            current_time = datetime.utcnow()
            expire_at = current_time + token_life
            
            # Log thời gian để debug
            logger.info(f"Token generation time (UTC): {current_time}")
            logger.info(f"Token expiration time (UTC): {expire_at}")
            logger.info(f"Token lifetime: {token_life.total_seconds()} seconds")
            
            payload = {**user_info, "exp": expire_at}
            token = jwt.encode(payload, secret_signature, algorithm="HS256")
            
            # Log token để debug
            logger.info(f"Generated token: {token}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            raise RuntimeError(f"Error generating token: {e}")

    @staticmethod
    def verify_token(token: str, secret_signature: str) -> dict:
        try:
            # Log thời gian hiện tại khi verify
            current_time = datetime.utcnow()
            logger.info(f"Verifying token at (UTC): {current_time}")
            
            decoded = jwt.decode(token, secret_signature, algorithms=["HS256"])
            
            # Log thời gian hết hạn của token
            if "exp" in decoded:
                exp_time = datetime.fromtimestamp(decoded["exp"])
                logger.info(f"Token expiration time (UTC): {exp_time}")
                logger.info(f"Time until expiration: {(exp_time - current_time).total_seconds()} seconds")
            
            return decoded
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            raise ValueError("Invalid token")
