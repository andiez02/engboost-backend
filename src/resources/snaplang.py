import io
import logging
from flask import jsonify, request
from PIL import Image, UnidentifiedImageError
from ultralytics import YOLO
from src.utils.translate import translate_word

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model YOLOv10 một lần khi khởi động server
model = YOLO("yolov10n.pt")

def detect_objects():
    
    if "image" not in request.files:
        logger.warning("No image uploaded in the request")
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]

    try:
        image = Image.open(io.BytesIO(image_file.read()))
    except UnidentifiedImageError:
        logger.error("Invalid image format")
        return jsonify({"error": "Invalid image format"}), 400

    logger.info("Image successfully loaded, running YOLOv10...")

    # Chạy YOLOv10 trên ảnh
    results = model(image)

    detections = []
    for result in results:
        for box in result.boxes:
            cls_id = int(box.cls[0])  # Lấy class ID
            name = result.names[cls_id]  # Lấy tên vật thể
            detections.append(name)

    if not detections:
        logger.info("No objects detected in the image")
        return jsonify({"message": "No objects detected"}), 200

    logger.info(f"Objects detected: {detections}")

    # Chuyển list thành set để loại bỏ trùng lặp
    unique_objects = set(detections)
    # Chuyển lại thành list nếu cần
    unique_objects = list(unique_objects)

    # Dịch tất cả các object sang tiếng Việt
    translated_objects = [
        {"object": obj, "english": obj.capitalize(), "vietnamese": translate_word(obj)}
        for obj in unique_objects
    ]

    return jsonify({"detections": translated_objects})
