from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from src.utils.api_error import ApiError
import logging

class CourseCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="")
    is_public: bool = Field(default=False)
    
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Course title is required')
        return v
    
    @field_validator('description')
    @classmethod
    def description_length(cls, v):
        if len(v) > 5000:
            raise ValueError('Description is too long (max 5000 characters)')
        return v
    
    class Config:
        # Allow extra attributes
        extra = "ignore"

class CourseUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None)
    is_public: Optional[bool] = None
    
    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Course title cannot be empty')
        return v
    
    @field_validator('description')
    @classmethod
    def description_length(cls, v):
        if v is not None and len(v) > 5000:
            raise ValueError('Description is too long (max 5000 characters)')
        return v
    
    class Config:
        # Allow extra attributes
        extra = "ignore"

def validate_course_creation(form_data):
    """Validate form data for course creation"""
    try:
        # Import Flask request để truy cập files
        from flask import request
        
        # Validate basic course data
        course_data = {
            "title": form_data.get("title", ""),
            "description": form_data.get("description", ""),
            "is_public": form_data.get("is_public", "false").lower() == "true"
        }
        CourseCreateSchema(**course_data)
        
        # Log form data và files
        logger = logging.getLogger(__name__)
        logger.info("Validating course creation with form keys: %s", list(form_data.keys()))
        logger.info("Request files keys: %s", list(request.files.keys()))
        
        # Check for required files with detailed error messages
        if "video" not in request.files:
            raise ApiError(400, "Video file is missing from the request")
            
        if not request.files["video"].filename:
            raise ApiError(400, "Video file was selected but has no filename")
            
        if "thumbnail" not in request.files:
            raise ApiError(400, "Thumbnail file is missing from the request")
            
        if not request.files["thumbnail"].filename:
            raise ApiError(400, "Thumbnail file was selected but has no filename")
            
        return True
    except ValueError as e:
        raise ApiError(400, str(e))

def validate_course_update(form_data):
    """Validate form data for course update"""
    try:
        # Validate update data
        update_data = {}
        
        if "title" in form_data:
            update_data["title"] = form_data.get("title")
        
        if "description" in form_data:
            update_data["description"] = form_data.get("description")
        
        if "is_public" in form_data:
            update_data["is_public"] = form_data.get("is_public", "false").lower() == "true"
        
        # Validate with pydantic model
        if update_data:
            CourseUpdateSchema(**update_data)
            
        return True
    except ValueError as e:
        raise ApiError(400, str(e)) 