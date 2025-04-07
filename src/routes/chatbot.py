from flask import Blueprint
from src.resources.chatbot import ChatbotResource

chatbot_bp = Blueprint("chatbot_bp", __name__)

@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    return ChatbotResource.chat()
