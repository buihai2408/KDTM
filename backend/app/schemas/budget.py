"""
Budget schemas
"""
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, Literal
from decimal import Decimal


class BudgetBase(BaseModel):
    """Base schema for budget"""
    category_id: int
    amount: Decimal
    month: int
    year: int
    
    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v
    
    @field_validator("month")
    @classmethod
    def month_must_be_valid(cls, v):
        if v < 1 or v > 12:
            raise ValueError("Month must be between 1 and 12")
        return v
    
    @field_validator("year")
    @classmethod
    def year_must_be_valid(cls, v):
        if v < 2020:
            raise ValueError("Year must be 2020 or later")
        return v


class BudgetCreate(BudgetBase):
    """Schema for creating a budget"""
    pass


class BudgetUpdate(BaseModel):
    """Schema for updating a budget"""
    amount: Optional[Decimal] = None
    
    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class BudgetResponse(BudgetBase):
    """Schema for budget response"""
    id: int
    user_id: int
    created_at: datetime
    
    # Include related data
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    category_color: Optional[str] = None
    
    class Config:
        from_attributes = True


class BudgetStatus(BaseModel):
    """Schema for budget status with actual spending"""
    id: int
    category_id: int
    category_name: str
    category_icon: str
    category_color: str
    budget_amount: Decimal
    actual_spent: Decimal
    remaining: Decimal
    usage_percentage: Decimal
    status: Literal["safe", "warning", "exceeded"]
    month: int
    year: int
