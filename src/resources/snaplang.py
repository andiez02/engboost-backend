import io
import logging
import os
import gc
import torch
from flask import jsonify, request
from PIL import Image, UnidentifiedImageError
from ultralytics import YOLO
from src.utils.translate import translate_word
from functools import lru_cache

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache kết quả dịch
@lru_cache(maxsize=100)
def cached_translate(word):
    try:
        return translate_word(word)
    except Exception as e:
        logger.error(f"Translation error for '{word}': {str(e)}")
        return "Không thể dịch"

# Lazy loading model - chỉ tải khi cần
model = None

def get_model():
    """Tải mô hình YOLOv8n (nhẹ nhất) với lazy loading"""
    global model
    
    if model is None:
        logger.info("Loading YOLOv8n model...")
        try:
            # Sử dụng YOLOv8n thay vì YOLOv10n
            model = YOLO("yolov8n.pt")
            
            # Tối ưu hóa mô hình cho inference
            model.to('cpu')
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise RuntimeError(f"Failed to load model: {str(e)}")
    
    return model

def preprocess_image(image_file):
    """Tiền xử lý ảnh đầu vào"""
    try:
        # Đọc và xử lý ảnh
        image_bytes = image_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Giảm kích thước ảnh nhiều hơn để tiết kiệm bộ nhớ
        max_size = 320  # Giảm xuống 320 thay vì 640
        if max(image.size) > max_size:
            logger.info(f"Resizing image from {image.size} to max dimension {max_size}")
            ratio = max_size / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.LANCZOS)
        
        return image
    except UnidentifiedImageError:
        logger.error("Invalid image format")
        raise ValueError("Invalid image format")
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise ValueError(f"Error processing image: {str(e)}")

def run_inference(model, image):
    """Chạy inference với mô hình YOLO"""
    try:
        # Cấu hình tham số để tối ưu hiệu suất và giảm bộ nhớ
        results = model(
            image,
            verbose=False,  # Tắt verbose để giảm log
            conf=0.4,       # Tăng ngưỡng tin cậy để giảm số lượng phát hiện
            iou=0.5,        # Tăng ngưỡng IoU
            max_det=10,     # Giảm số lượng phát hiện tối đa
            device='cpu'    # Chỉ định thiết bị
        )
        return results
    except Exception as e:
        logger.error(f"Error during model inference: {str(e)}")
        raise RuntimeError(f"Error running model: {str(e)}")
    finally:
        # Giải phóng bộ nhớ cache của PyTorch
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        gc.collect()

def detect_objects():
    """Hàm chính để phát hiện đối tượng trong ảnh"""
    # Kiểm tra request
    if "image" not in request.files:
        logger.warning("No image uploaded in the request")
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    
    # Tiền xử lý ảnh
    try:
        image = preprocess_image(image_file)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    logger.info("Image successfully loaded, running YOLO model...")
    
    try:
        # Lấy mô hình (lazy loading)
        yolo_model = get_model()
        
        # Chạy inference
        results = run_inference(yolo_model, image)
        
        # Xử lý kết quả
        detections = []
        for result in results:
            boxes = result.boxes
            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i].item())  # Lấy class ID
                conf = float(boxes.conf[i].item())  # Lấy độ tin cậy
                
                # Chỉ lấy các dự đoán có độ tin cậy cao
                if conf >= 0.4:
                    name = result.names[cls_id]  # Lấy tên vật thể
                    detections.append(name)
    except Exception as e:
        logger.error(f"Error in object detection: {str(e)}")
        return jsonify({"error": "Failed to detect objects in image"}), 500
    finally:
        # Giải phóng bộ nhớ
        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
    
    if not detections:
        logger.info("No objects detected in the image")
        return jsonify({"message": "No objects detected"}), 200
    
    logger.info(f"Objects detected: {detections}")
    
    # Chuyển list thành set để loại bỏ trùng lặp
    unique_objects = list(set(detections))
    
    # Dịch tất cả các object sang tiếng Việt
    translated_objects = [
        {"object": obj, "english": obj.capitalize(), "vietnamese": cached_translate(obj)}
        for obj in unique_objects
    ]
    
    return jsonify({"detections": translated_objects})
