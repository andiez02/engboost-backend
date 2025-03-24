from flask import Blueprint
from src.resources.snaplang import detect_objects

snaplang_bp = Blueprint("snaplang", __name__)

snaplang_bp.route("/detect", methods=["POST"])(detect_objects)
