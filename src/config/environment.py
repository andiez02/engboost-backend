import os
from dotenv import load_dotenv
from datetime import timedelta

# Load biến môi trường từ file .env
load_dotenv()

class EnvConfig:
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", 5000))

WEBSITE_DOMAIN = os.getenv("WEBSITE_DOMAIN")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
ADMIN_EMAIL_ADDRESS = os.getenv("ADMIN_EMAIL_ADDRESS")
ADMIN_EMAIL_NAME = os.getenv("ADMIN_EMAIL_NAME")

ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
REFRESH_TOKEN_SECRET = os.getenv("REFRESH_TOKEN_SECRET")
ACCESS_TOKEN_LIFE = timedelta(minutes=60)   
REFRESH_TOKEN_LIFE = timedelta(days=15)    
