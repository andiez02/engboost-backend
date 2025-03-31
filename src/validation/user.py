from typing import Optional
from pydantic import BaseModel, EmailStr, Field, model_validator
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
    token: str = Field(...)


class LoginValidation(BaseModel):
    email: EmailStr = Field(..., pattern=EMAIL_RULE.pattern, description=EMAIL_RULE_MESSAGE)  
    password: str = Field(..., min_length=8, description=PASSWORD_RULE_MESSAGE)


class UserSchema(BaseModel):
    email: EmailStr = Field(..., pattern=EMAIL_RULE.pattern, description=EMAIL_RULE_MESSAGE)
    password: str = Field(..., min_length=8, description=PASSWORD_RULE_MESSAGE)


class UpdateUserValidation(BaseModel):
    username: str = Field(default=None, exclude_unset=True)
    current_password: str = Field(default=None, exclude_unset=True)
    new_password: str = Field(default=None, exclude_unset=True)
    avatar: str = Field(default=None, exclude_unset=True)

    class Config:
        extra = "allow"

    @model_validator(mode="after")
    def validate_passwords(self) -> "UpdateUserValidation":
        if self.new_password and not self.current_password:
            raise ValueError("Current password is required when setting a new password")
        return self
