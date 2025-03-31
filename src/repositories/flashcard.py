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
        
        deleted_flashcard = FlashcardModel.delete(flashcard_id)
        
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
                "title": folder_title.strip(),
                "user_id": user_id
            }
            
            logger.info(f"Creating new folder with title: {folder_title}")
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
                    if card.get("image_url"):
                        image_source = card["image_url"]
                        logger.info(f"Found image_url: {image_source[:30]}...")
                    elif card.get("imageUrl"):
                        image_source = card["imageUrl"]
                        logger.info(f"Found imageUrl: {image_source[:30]}...")
                    else:
                        image_source = None
                        logger.info("No image field found in card")
                    
                    # Process image if exists
                    if image_source and isinstance(image_source, str) and image_source.startswith("data:"):
                        try:
                            logger.info("Uploading image to Cloudinary...")
                            upload_result = CloudinaryService.upload_image(image_source)
                            image_url = upload_result["url"]
                            logger.info(f"Successfully uploaded image: {image_url}")
                        except Exception as e:
                            logger.error(f"Error uploading image: {str(e)}")
                            invalid_flashcards.append({
                                "index": i + idx,
                                "card": card,
                                "error": f"Error uploading image: {str(e)}"
                            })
                            continue
                    elif image_source and isinstance(image_source, str) and (image_source.startswith("http://") or image_source.startswith("https://")):
                        image_url = image_source
                        logger.info(f"Using existing image URL: {image_url}")
                    
                    # Create flashcard data
                    flashcard_data = {
                        "english": card.get("english"),
                        "vietnamese": card.get("vietnamese"),
                        "object": card.get("object"),
                        "image_url": image_url,
                        "folder_id": folder_id,
                        "user_id": user_id,
                        "created_at": datetime.utcnow()
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
        if valid_flashcards:
            try:
                # Use bulk insert for better performance
                logger.info(f"Inserting {len(valid_flashcards)} flashcards into database...")
                result = FlashcardModel.bulk_insert(valid_flashcards)
                imported_count = len(valid_flashcards)
                logger.info(f"Successfully inserted {imported_count} flashcards into folder {folder_id}")
                
                # Update folder flashcard count
                FolderModel.increment_flashcard_count(folder_id, increment=imported_count)
            except Exception as e:
                logger.error(f"Error during bulk import: {str(e)}")
                raise ApiError(500, "Error during bulk import")
        
        # Step 4: Return result
        return {
            "folder_id": folder_id,
            "imported_count": imported_count,
            "invalid_count": len(invalid_flashcards),
            "invalid_flashcards": invalid_flashcards
        }