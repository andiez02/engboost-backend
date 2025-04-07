# src/config/mongodb.py
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.server_api import ServerApi
from src.config.environment import EnvConfig
import logging
import certifi
from flask import g, current_app

class MongoDB:
    client = None
    db = None
    
    @classmethod
    def connect(cls):
        if cls.client is None:
            print(f"🔄 Connecting to MongoDB with URI")
            # Cấu hình connection pooling
            cls.client = MongoClient(
                EnvConfig.MONGO_URI, 
                server_api=ServerApi('1'), 
                tlsCAFile=certifi.where(),
                maxPoolSize=50,  # Tăng kích thước pool
                minPoolSize=10,  # Duy trì ít nhất 10 kết nối
                maxIdleTimeMS=30000,  # Đóng kết nối không hoạt động sau 30 giây
                connectTimeoutMS=5000,  # Timeout kết nối 5 giây
                socketTimeoutMS=30000,  # Timeout socket 30 giây
                waitQueueTimeoutMS=10000  # Timeout hàng đợi 10 giây
            )
            cls.db = cls.client.get_database(EnvConfig.MONGO_DB_NAME)
            try:
                cls.client.admin.command('ping')
                print("✅ Connected to MongoDB Atlas successfully!")
                # Tạo indexes khi kết nối thành công
                cls.create_indexes()
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
            users_collection = cls.db.users
            
            # Lấy danh sách index hiện có
            existing_indexes = users_collection.index_information()
            
            # Tạo index nếu chưa tồn tại
            if "username_1" not in existing_indexes:
                users_collection.create_index([("username", ASCENDING)], background=True)
            
            if "email_1" not in existing_indexes:
                users_collection.create_index([("email", ASCENDING)], background=True)
            
            if "role_1" not in existing_indexes:
                users_collection.create_index([("role", ASCENDING)], background=True)
            
            if "user_text_search" not in existing_indexes:
                users_collection.create_index([
                    ("username", TEXT),
                    ("email", TEXT),
                    ("fullName", TEXT)
                ], name="user_text_search", background=True)
            
            print("✅ MongoDB indexes created successfully!")
        except Exception as e:
            logging.error(f"❌ Failed to create indexes: {e}")
            print(f"❌ Failed to create indexes: {e}")
