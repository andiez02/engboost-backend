from src.models.flashcard import FlashcardModel
from src.models.folder import FolderModel
from src.utils.api_error import ApiError
from src.utils.error_handlers import repo_error_handler
from src.utils.mongo_helper import serialize_mongo_data
from src.config.cloudinary import CloudinaryService
import logging

class FlashcardRepository:
    @staticmethod
    @repo_error_handler
    def get_flashcards_by_folder(folder_id, user_id):
        folder = FolderModel.find_by_id(folder_id)
        if not folder:
            raise ApiError(404, "Folder not found")
            
        if folder["user_id"] != user_id and not folder.get("is_public", False):
            raise ApiError(403, "You don't have permission to access this folder")
            
        flashcards = FlashcardModel.find_by_folder(folder_id)
        serialized_flashcards = [serialize_mongo_data(flashcard) for flashcard in flashcards]
        
        return serialized_flashcards

    @staticmethod
    @repo_error_handler
    def get_flashcard_by_id(flashcard_id, user_id):
        flashcard = FlashcardModel.find_by_id(flashcard_id)
        folder = FolderModel.find_by_id(flashcard["folder_id"])
        if not folder:
            raise ApiError(404, "Folder not found")
            
        if folder["user_id"] != user_id and not folder.get("is_public", False):
            raise ApiError(403, "You don't have permission to access this flashcard")
            
        return serialize_mongo_data(flashcard)

    @staticmethod
    @repo_error_handler
    def delete_flashcard(flashcard_id, user_id):
        flashcard = FlashcardModel.find_by_id(flashcard_id)
        folder = FolderModel.find_by_id(flashcard["folder_id"])
        if folder["user_id"] != user_id:
            raise ApiError(403, "You don't have permission to delete this flashcard")
        
        if flashcard.get("image_url"):
            CloudinaryService.delete_image(flashcard["image_url"])
        
        # Xóa flashcard
        deleted_flashcard = FlashcardModel.delete(flashcard_id)
        
        # Đếm số lượng flashcard còn lại trong folder
        remaining_flashcards = FlashcardModel.count_by_folder(flashcard["folder_id"])
        
        # Cập nhật flashcard_count của folder dựa trên số lượng thực tế
        FolderModel.update_flashcard_count(flashcard["folder_id"], remaining_flashcards)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Updated folder {flashcard['folder_id']} flashcard_count to {remaining_flashcards}")
        
        return serialize_mongo_data(deleted_flashcard)

    @staticmethod
    @repo_error_handler
    def save_flashcards_to_folder(create_new_folder, folder_id, folder_title, flashcards_data, user_id):
            """Save flashcards to a folder (new or existing)"""
            from datetime import datetime
            import logging
            logger = logging.getLogger(__name__)
            
            # Debug request data
            logger.info("====== FLASHCARD IMPORT REQUEST ======")
            logger.info(f"Create new folder: {create_new_folder}")
            logger.info(f"Folder ID: {folder_id}")
            logger.info(f"Folder title: {folder_title}")
            logger.info(f"Flashcards count: {len(flashcards_data)}")
            logger.info(f"Sample flashcard: {flashcards_data[0] if flashcards_data else 'None'}")
            
            # Step 1: Handle folder creation or validation
            if create_new_folder:
                # Create a new folder
                from src.repositories.folder import FolderRepository
                folder_data = {
                    "title": folder_title.strip() if folder_title else "Untitled Folder",
                    "user_id": user_id,
                    "is_public": False,
                    "flashcard_count": 0,
                    "created_at": datetime.utcnow()
                }
                
                logger.info(f"Creating new folder with title: {folder_data['title']}")
                folder_result = FolderRepository.create_new(folder_data)
                folder_id = folder_result["_id"]
                logger.info(f"Created new folder with ID: {folder_id}")
            else:
                # Validate existing folder
                folder = FolderModel.find_by_id(folder_id)
                if not folder:
                    raise ApiError(404, "Folder not found")
                    
                if folder["user_id"] != user_id:
                    raise ApiError(403, "You don't have permission to add flashcards to this folder")
            
            # Step 2: Process flashcards
            valid_flashcards = []
            invalid_flashcards = []
            
            # Process flashcards in batches for better performance
            batch_size = 100
            for i in range(0, len(flashcards_data), batch_size):
                batch = flashcards_data[i:i + batch_size]
                for idx, card in enumerate(batch):
                    try:
                        # Debug the card data
                        logger.info(f"Processing card {i+idx}: {card}")
                        
                        # Validate required fields
                        if not card.get("english") or not card.get("vietnamese"):
                            logger.warning(f"Missing required fields for card {i+idx}")
                            invalid_flashcards.append({
                                "index": i + idx,
                                "card": card,
                                "error": "English and Vietnamese fields are required"
                            })
                            continue
                        
                        # Handle image upload if present
                        image_url = None
                        # Check multiple possible image field names
                        image_source = None
                        for field in ["image_url", "imageUrl", "image_data", "imageData", "image"]:
                            if field in card and card[field]:
                                image_source = card[field]
                                logger.info(f"Found image in field '{field}': {image_source[:30] if isinstance(image_source, str) else 'Non-string data'}...")
                                break
                        
                        # Process image if exists
                        if image_source and isinstance(image_source, str):
                            if image_source.startswith("data:"):
                                try:
                                    logger.info("Uploading image to Cloudinary...")
                                    # Use the folder parameter that your service accepts
                                    folder_path = f"flashcards/{user_id}"
                                    upload_result = CloudinaryService.upload_image(image_source, folder=folder_path)
                                    image_url = upload_result["url"]
                                    logger.info(f"Successfully uploaded image: {image_url}")
                                except Exception as e:
                                    logger.error(f"Error uploading image: {str(e)}")
                                    # Continue with the flashcard but without image
                                    logger.warning("Continuing without image due to upload error")
                            elif image_source.startswith("http://") or image_source.startswith("https://"):
                                image_url = image_source
                                logger.info(f"Using existing image URL: {image_url}")
                        
                        # Create flashcard data
                        flashcard_data = {
                            "english": card.get("english").strip() if card.get("english") else "",
                            "vietnamese": card.get("vietnamese").strip() if card.get("vietnamese") else "",
                            "object": card.get("object", "").strip() if card.get("object") else None,
                            "image_url": image_url,
                            "folder_id": folder_id,
                            "user_id": user_id,
                            "is_public": False,
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow(),
                            "status": "active"
                        }
                        
                        logger.info(f"Created flashcard data: {flashcard_data}")
                        valid_flashcards.append(flashcard_data)
                        
                    except Exception as e:
                        logger.error(f"Error processing flashcard: {str(e)}")
                        invalid_flashcards.append({
                            "index": i + idx,
                            "card": card,
                            "error": str(e)
                        })
            
            # Step 3: Insert valid flashcards
            imported_count = 0
            inserted_flashcards = []
            if valid_flashcards:
                try:
                    # Use bulk insert for better performance
                    logger.info(f"Inserting {len(valid_flashcards)} flashcards into database...")
                    result = FlashcardModel.bulk_insert(valid_flashcards)
                    imported_count = len(valid_flashcards)
                    logger.info(f"Successfully inserted {imported_count} flashcards into folder {folder_id}")
                    
                    # Update folder flashcard count
                    FolderModel.increment_flashcard_count(folder_id, increment=imported_count)
                    
                    # Get the inserted flashcards for response
                    inserted_flashcards = valid_flashcards
                    for flashcard in inserted_flashcards:
                        # Convert ObjectId to string for JSON serialization
                        if "_id" in flashcard and flashcard["_id"]:
                            flashcard["_id"] = str(flashcard["_id"])
                        flashcard["folder_id"] = str(flashcard["folder_id"])
                        flashcard["user_id"] = str(flashcard["user_id"])
                        
                        # Format dates for JSON serialization
                        if "created_at" in flashcard and flashcard["created_at"]:
                            flashcard["created_at"] = flashcard["created_at"].isoformat()
                        if "updated_at" in flashcard and flashcard["updated_at"]:
                            flashcard["updated_at"] = flashcard["updated_at"].isoformat()
                        
                except Exception as e:
                    logger.error(f"Error during bulk import: {str(e)}")
                    raise ApiError(500, f"Error during bulk import: {str(e)}")
            
            # Step 4: Return result
            return {
                "folder_id": str(folder_id),
                "imported_count": imported_count,
                "invalid_count": len(invalid_flashcards),
                "invalid_flashcards": invalid_flashcards,
                "flashcards": inserted_flashcards
            }
