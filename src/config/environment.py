import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

class EnvConfig:
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
    APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT = int(os.getenv("APP_PORT", 5000))


