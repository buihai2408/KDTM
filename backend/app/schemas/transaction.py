"""
Transaction schemas
"""
from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional, Literal
from decimal import Decimal


class TransactionBase(BaseModel):
    """Base schema for transaction"""
    wallet_id: int
    category_id: int
    type: Literal["income", "expense"]
    amount: Decimal
    description: Optional[str] = None
    transaction_date: date
    
    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction"""
    pass


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction"""
    wallet_id: Optional[int] = None
    category_id: Optional[int] = None
    type: Optional[Literal["income", "expense"]] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    transaction_date: Optional[date] = None
    
    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class TransactionResponse(TransactionBase):
    """Schema for transaction response"""
    id: int
    user_id: int
    created_at: datetime
    
    # Include related data
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    category_color: Optional[str] = None
    wallet_name: Optional[str] = None
    
    class Config:
        from_attributes = True
