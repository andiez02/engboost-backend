from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Dict, Any

class FlashcardSchema(BaseModel):
    english: str = Field(..., min_length=1, max_length=200)
    vietnamese: str = Field(..., min_length=1, max_length=200)
    object: str | None = None
    image_url: str | None = None
    imageUrl: str | None = None  # Alternative field name from client

    @field_validator('english', 'vietnamese')
    @classmethod
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError('Field cannot be empty')
        return v
    
    @model_validator(mode='after')
    def normalize_image_url(self) -> 'FlashcardSchema':
        # Prioritize image_url, but if it's None, use imageUrl
        if self.image_url is None and self.imageUrl is not None:
            self.image_url = self.imageUrl
        # Always set imageUrl to None to avoid confusion
        self.imageUrl = None
        return self

    class Config:
        # Allow extra attributes
        extra = "ignore"

class SaveFlashcardsValidation(BaseModel):
    create_new_folder: bool = Field(default=False)
    folder_id: str | None = None
    folder_title: str | None = None
    flashcards: List[FlashcardSchema] = Field(..., min_items=1)

    @field_validator('folder_title')
    @classmethod
    def validate_folder_title(cls, v, info):
        if info.data.get('create_new_folder') and (not v or not v.strip()):
            raise ValueError('Folder title is required when creating a new folder')
        return v

    @field_validator('folder_id')
    @classmethod
    def validate_folder_id(cls, v, info):
        if not info.data.get('create_new_folder') and not v:
            raise ValueError('Folder ID is required when using existing folder')
        return v
    
    class Config:
        # Allow extra attributes
        extra = "ignore" 