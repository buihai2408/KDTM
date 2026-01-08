"""
Bill model for recurring bills tracking
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Bill(Base):
    """Bill model for tracking recurring bills"""
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.id", ondelete="RESTRICT"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String(200), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    due_day = Column(Integer, nullable=False)  # Day of month (1-31)
    is_recurring = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="bills")
    wallet = relationship("Wallet", backref="bills")
    category = relationship("Category", backref="bills")
