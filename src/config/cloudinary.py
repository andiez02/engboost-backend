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
    
    @staticmethod
    def upload_video(video_file, folder="courses"):
        """Upload video lên Cloudinary"""
        try:
            # Upload video với các tùy chọn phù hợp cho streaming
            result = cloudinary.uploader.upload(
                video_file,
                folder=folder,
                resource_type="video",
                eager=[
                    # Tạo các biến thể video với chất lượng khác nhau
                    {"streaming_profile": "hd", "format": "m3u8"},
                ],
                eager_async=True,  # Xử lý bất đồng bộ để tránh timeout
                eager_notification_url=os.getenv("CLOUDINARY_NOTIFICATION_URL", ""),
            )
            
            # Trả về thông tin video đã upload
            return {
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "duration": result.get("duration", 0),
                "format": result.get("format", ""),
                "resource_type": result.get("resource_type", "video")
            }
        except Exception as e:
            print(f"Error uploading video to Cloudinary: {str(e)}")
            raise
            
    @staticmethod
    def delete_video(public_id):
        """Xóa video từ Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id, resource_type="video")
            return result
        except Exception as e:
            print(f"Error deleting video from Cloudinary: {str(e)}")
            # Không raise lỗi để tránh ảnh hưởng đến flow chính
            return {"result": "error", "error": str(e)} 