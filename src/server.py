from flask import Flask
from src.routes import api_bp
from src.config.environment import EnvConfig
from src.config.mongodb import MongoDB
from src.middleware.error_handling import error_handling_middleware
import atexit
from flask_cors import CORS
import logging
import os

app = Flask(__name__)

# Kiểm tra môi trường
is_production = os.environ.get('FLASK_ENV') == 'production'

# Cấu hình CORS dựa trên môi trường
if is_production:
    # Môi trường production
    CORS(app, 
         supports_credentials=True, 
         origins=["https://engboost-frontend.onrender.com"])
    app.config["DEBUG"] = False
else:
    # Môi trường development
    CORS(app, 
         supports_credentials=True, 
         origins=["http://localhost:5173"])
    app.config["DEBUG"] = True

# Cấu hình cho upload file lớn (500MB)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# Cấu hình logging dựa trên môi trường
if is_production:
    logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.INFO)

# Đăng ký middleware xử lý lỗi
error_handling_middleware(app)

# Đăng ký Blueprint
app.register_blueprint(api_bp)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/")
def home():
    return {"message": "Welcome to Flask API with MongoDB", "environment": "production" if is_production else "development"}

# Kết nối DB khi server khởi động
MongoDB.connect()

# Đóng DB khi server tắt
atexit.register(MongoDB.close)

if __name__ == "__main__":
    # Cấu hình host và port dựa trên môi trường
    if is_production:
        # Trong production, sử dụng PORT từ biến môi trường hoặc mặc định 10000
        port = int(os.environ.get("PORT", 10000))
        host = "0.0.0.0"  # Bind đến tất cả các interface
    else:
        # Trong development, sử dụng cấu hình từ EnvConfig
        port = EnvConfig.APP_PORT
        host = "localhost"
    
    app.run(host=host, port=port, debug=not is_production)
