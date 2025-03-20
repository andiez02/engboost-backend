from pymongo import MongoClient
from pymongo.server_api import ServerApi
from src.config.environment import EnvConfig
import certifi

class MongoDB:
    client = None
    db = None

    @classmethod
    def connect(cls):
        if cls.client is None:
            print(f"🔄 Connecting to MongoDB with URI: {EnvConfig.MONGO_URI}")  
            cls.client = MongoClient(EnvConfig.MONGO_URI, server_api=ServerApi('1'), tlsCAFile=certifi.where())
            cls.db = cls.client.get_database(EnvConfig.MONGO_DB_NAME)
            try:
                cls.client.admin.command('ping')
                print("✅ Connected to MongoDB Atlas successfully!")
            except Exception as e:
                print(f"❌ Connection failed: {e}")

    @classmethod
    def get_db(cls):
        if cls.db is None:
            cls.connect()
        return cls.db

    @classmethod
    def close(cls):
        if cls.client:
            cls.client.close()
            print("🛑 MongoDB connection closed.")
