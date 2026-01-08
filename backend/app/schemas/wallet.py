"""
Wallet schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal


class WalletBase(BaseModel):
    """Base schema for wallet"""
    name: str
    currency: Optional[str] = "VND"
    icon: Optional[str] = "wallet"


class WalletCreate(WalletBase):
    """Schema for creating a wallet"""
    initial_balance: Optional[Decimal] = Decimal("0")


class WalletUpdate(BaseModel):
    """Schema for updating a wallet"""
    name: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None


class WalletResponse(WalletBase):
    """Schema for wallet response"""
    id: int
    user_id: int
    balance: Decimal
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
