project_root/
│── src/
│ ├── config/ # Chứa các file cấu hình
│ │ ├── environment.py # Load biến môi trường từ .env
│ │ ├── mongodb.py # Kết nối MongoDB
│ ├── models/ # Định nghĩa model
│ │ ├── abc.py
│ │ └── user.py
│ ├── repositories/ # Tầng repository
│ │ └── user.py
│ ├── resources/ # Xử lý logic request
│ │ └── user.py
│ ├── routes/ # Định nghĩa routes
│ │ ├── **init**.py
│ │ └── user.py
│ ├── util/ # Các hàm helper
│ │ └── parse_params.py
│ ├── server.py # Khởi động Flask server
│ ├── manage.py # Command-line tool (tuỳ chọn)
│── .env # Biến môi trường
│── requirements.txt # Danh sách package Python

First Time Run: export PYTHONPATH=$(pwd)
python src/server.py
x