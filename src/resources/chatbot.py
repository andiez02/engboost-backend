# src/resources/chatbot.py
from flask import request, jsonify
import google.generativeai as genai
import os
import logging

class ChatbotResource:
    @staticmethod
    def chat():
        try:
            if not request.is_json:
                return jsonify({"error": "Yêu cầu phải là JSON"}), 400

            data = request.get_json()
            user_message = data.get('message')

            if not user_message:
                return jsonify({"error": "Không tìm thấy tin nhắn"}), 400

            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                logging.error("GOOGLE_API_KEY không được thiết lập")
                return jsonify({"error": "Cấu hình server không đúng"}), 500

            genai.configure(api_key=api_key)

            # Sử dụng mô hình đúng
            model_id = 'gemini-2.0-flash-exp'
            model = genai.GenerativeModel(model_id)

            prompt = f"""
            Bạn là trợ lý học tiếng Anh của EngBoost. Hãy giúp người dùng học tiếng Anh hiệu quả.
            Nếu người dùng hỏi về từ vựng, hãy cung cấp định nghĩa, ví dụ, và cách sử dụng.
            Nếu người dùng hỏi về ngữ pháp, hãy giải thích rõ ràng với ví dụ cụ thể.
            Nếu người dùng yêu cầu dịch, hãy cung cấp bản dịch chính xác và tự nhiên.

            Câu hỏi của người dùng: {user_message}
            """

            response = model.generate_content(prompt)

            if response and hasattr(response, 'text'):
                return jsonify({"reply": response.text})
            else:
                return jsonify({"reply": "Xin lỗi, tôi không thể tạo phản hồi lúc này."})

        except Exception as e:
            logging.exception(f"Lỗi khi gọi Gemini API: {str(e)}")
            return jsonify({"error": f"Lỗi server: {str(e)}"}), 500
