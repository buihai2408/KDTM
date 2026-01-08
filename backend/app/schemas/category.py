"""
Category schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal


class CategoryBase(BaseModel):
    """Base schema for category"""
    name: str
    type: Literal["income", "expense"]
    icon: Optional[str] = "tag"
    color: Optional[str] = "#6366f1"


class CategoryCreate(CategoryBase):
    """Schema for creating a category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema for category response"""
    id: int
    user_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
