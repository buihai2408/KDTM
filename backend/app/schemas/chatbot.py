"""
Chatbot API Schemas
Pydantic models for Dify Cloud integration
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class ChatbotQueryRequest(BaseModel):
    """Request schema for chatbot query endpoint"""
    user_id: int = Field(..., description="User ID to filter data")
    question: str = Field(..., description="User's question in Vietnamese or English")
    timezone: str = Field(default="Asia/Bangkok", description="User's timezone")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "question": "Tổng chi tiêu tháng này là bao nhiêu?",
                "timezone": "Asia/Bangkok"
            }
        }


class ChatbotQueryResponse(BaseModel):
    """Response schema for chatbot query endpoint"""
    answer: str = Field(..., description="Natural language answer to the question")
    data: Optional[Any] = Field(None, description="Structured data (if applicable)")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested follow-up actions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Tổng chi tiêu tháng 1/2026 của bạn là 5,500,000 VND",
                "data": {
                    "total_expense": 5500000,
                    "month": 1,
                    "year": 2026,
                    "currency": "VND"
                },
                "suggested_actions": [
                    "Xem chi tiết theo danh mục",
                    "So sánh với tháng trước",
                    "Kiểm tra ngân sách"
                ]
            }
        }


class ChatbotHealthResponse(BaseModel):
    """Response schema for health check endpoint"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    timestamp: str = Field(..., description="Current timestamp")
    available_views: List[str] = Field(..., description="List of available BI views")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "chatbot",
                "timestamp": "2026-01-09T10:00:00",
                "available_views": [
                    "v_income_vs_expense",
                    "v_monthly_summary",
                    "v_category_breakdown"
                ]
            }
        }


class QueryResultResponse(BaseModel):
    """Response schema for structured query results"""
    query_type: str = Field(..., description="Type of query executed")
    rows: List[dict] = Field(default_factory=list, description="Query result rows")
    row_count: int = Field(..., description="Number of rows returned")
    metadata: Optional[dict] = Field(None, description="Additional metadata")
