from flask import Flask
from src.routes import api_bp
from src.config.environment import EnvConfig
from src.config.mongodb import MongoDB
from middleware.error_handling import error_handling_middleware
import atexit
from flask_cors import CORS
from flask import jsonify



app = Flask(__name__)
# Cấu hình CORS
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
app.config["DEBUG"] = True 

# Đăng ký middleware xử lý lỗi
error_handling_middleware(app)

# Đăng ký Blueprint
app.register_blueprint(api_bp)

@app.route("/")
def home():
    return jsonify({"message": "Welcome to Flask API with MongoDB"})

# Kết nối DB khi server khởi động
MongoDB.connect()

# Đóng DB khi server tắt
atexit.register(MongoDB.close)

if __name__ == "__main__":
    app.run(host="localhost", port=EnvConfig.APP_PORT, debug=True)
