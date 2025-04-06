from flask import Flask
from src.routes import api_bp
from src.config.environment import EnvConfig
from src.config.mongodb import MongoDB
from middleware.error_handling import error_handling_middleware
import atexit
from flask_cors import CORS
import logging

app = Flask(__name__)
# Cấu hình CORS
CORS(app, supports_credentials=True)  
app.config["DEBUG"] = True 

# Cấu hình cho upload file lớn (500MB)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# Cấu hình logging
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
    return {"message": "Welcome to Flask API with MongoDB"}

# Kết nối DB khi server khởi động
MongoDB.connect()

# Đóng DB khi server tắt
atexit.register(MongoDB.close)

if __name__ == "__main__":
    app.run(host="localhost", port=EnvConfig.APP_PORT, debug=True)
