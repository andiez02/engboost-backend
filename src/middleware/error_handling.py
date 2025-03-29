from flask import jsonify
from src.utils.api_error import ApiError

def error_handling_middleware(app):
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        response = {
            "statusCode": error.status_code,
            "message": error.message 
        }
        return jsonify(response), error.status_code

    @app.errorhandler(Exception)
    def handle_general_error(error):
        print(f"Unexpected Error: {error}")  
        response = {
            "statusCode": 500,
            "message": str(error) if app.config["DEBUG"] else "Something went wrong!"
        }
        return jsonify(response), 500
