from flask import Flask
from src.routes import api_bp
from src.config.environment import EnvConfig
from src.config.mongodb import MongoDB
import atexit
from flask_cors import CORS

app = Flask(__name__)
# Cấu hình CORS
CORS(app, supports_credentials=True)


# Đăng ký Blueprint
app.register_blueprint(api_bp)

@app.route("/")
def home():
    return {"message": "Welcome to Flask API with MongoDB"}

# Kết nối DB khi server khởi động
MongoDB.connect()

# Đóng DB khi server tắt
atexit.register(MongoDB.close)

if __name__ == "__main__":
    # print(f"🚀 Server is running at http://{EnvConfig.APP_HOST}:{EnvConfig.APP_PORT}")
    app.run(host=EnvConfig.APP_HOST, port=EnvConfig.APP_PORT, debug=True)
