"""
Bill schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class BillBase(BaseModel):
    """Base bill schema"""
    name: str = Field(..., min_length=1, max_length=200)
    amount: Decimal = Field(..., gt=0)
    due_day: int = Field(..., ge=1, le=31)
    description: Optional[str] = None
    is_recurring: bool = True


class BillCreate(BillBase):
    """Schema for creating a bill"""
    wallet_id: int
    category_id: int


class BillUpdate(BaseModel):
    """Schema for updating a bill"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[Decimal] = Field(None, gt=0)
    due_day: Optional[int] = Field(None, ge=1, le=31)
    wallet_id: Optional[int] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    is_recurring: Optional[bool] = None
    is_active: Optional[bool] = None


class BillResponse(BillBase):
    """Schema for bill response"""
    id: int
    user_id: int
    wallet_id: int
    category_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UpcomingBillResponse(BaseModel):
    """Schema for upcoming bill with details"""
    bill_id: int
    user_id: int
    user_email: str
    user_name: str
    bill_name: str
    amount: Decimal
    due_day: int
    due_date: str  # Computed due date for the month
    description: Optional[str]
    wallet_name: str
    currency: str
    category_name: str

    class Config:
        from_attributes = True
