from pydantic import BaseModel, Field, validator

class CreateFolderValidation(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="")
    is_public: bool = Field(default=False, alias="isPublic")

    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v
    
    class Config:
        populate_by_name = True

class UpdateFolderValidation(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    is_public: bool | None = Field(None, alias="isPublic")

    @validator('title')
    def title_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v
    
    class Config:
        populate_by_name = True 