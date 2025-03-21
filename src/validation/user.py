from pydantic import BaseModel, EmailStr, Field
from src.utils.constants import (
    EMAIL_RULE,
    EMAIL_RULE_MESSAGE,
    PASSWORD_RULE,
    PASSWORD_RULE_MESSAGE,
)


class UserSchema(BaseModel):
    email: EmailStr = Field(..., pattern=EMAIL_RULE.pattern, description=EMAIL_RULE_MESSAGE)
    password: str = Field(..., min_length=8, description=PASSWORD_RULE_MESSAGE)
