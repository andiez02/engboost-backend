import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

class CloudinaryService:
    @staticmethod
    def upload_image(base64_image, folder="flashcards"):
        """Upload ảnh lên Cloudinary từ base64 string"""
        try:
            # Upload ảnh
            result = cloudinary.uploader.upload(
                base64_image,
                folder=folder,
                resource_type="image"
            )
            
            # Trả về URL của ảnh
            return {
                "url": result["secure_url"],
                "public_id": result["public_id"]
            }
        except Exception as e:
            print(f"Error uploading to Cloudinary: {str(e)}")
            raise
    
    @staticmethod
    def delete_image(public_id):
        """Xóa ảnh từ Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result
        except Exception as e:
            print(f"Error deleting from Cloudinary: {str(e)}")
            # Không raise lỗi để tránh ảnh hưởng đến flow chính
            return {"result": "error", "error": str(e)} 