from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.server_api import ServerApi
from src.config.environment import EnvConfig
import logging
import certifi

class MongoDB:
    client = None
    db = None

    @classmethod
    def connect(cls):
        if cls.client is None:
            print(f"🔄 Connecting to MongoDB with URI")  
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

    @classmethod
    def create_indexes(cls):
        """
        Tạo các index cần thiết cho các collection trong database.
        """
        try:
            # Tạo index cho collection users
            users_collection = cls.db.users

            # Index cho tìm kiếm người dùng
            users_collection.create_index([("username", ASCENDING)])
            users_collection.create_index([("email", ASCENDING)])
            users_collection.create_index([("role", ASCENDING)])

            # Index text cho tìm kiếm full-text
            users_collection.create_index([
                ("username", TEXT),
                ("email", TEXT),
                ("fullName", TEXT)
            ], name="user_text_search")

            # Tạo index cho các collection khác nếu cần
            # folders_collection = cls.db.folders
            # folders_collection.create_index([("userId", ASCENDING)])

            # flashcards_collection = cls.db.flashcards
            # flashcards_collection.create_index([("folderId", ASCENDING)])

            print("✅ MongoDB indexes created successfully!")
        except Exception as e:
            logging.error(f"❌ Failed to create indexes: {e}")
            print(f"❌ Failed to create indexes: {e}")