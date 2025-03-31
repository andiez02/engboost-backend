import re

FIELD_REQUIRED_MESSAGE = "This field is required"
EMAIL_RULE = re.compile(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$")
EMAIL_RULE_MESSAGE = "Email is invalid."
PASSWORD_RULE = re.compile(r"^.{8,}$")
PASSWORD_RULE_MESSAGE = (
    "Password must at least 8 characters."
)

LIMIT_COMMON_FILE_SIZE = 10485760;
ALLOW_COMMON_FILE_TYPE = ["image/jpg", "image/jpeg", "image/png"];