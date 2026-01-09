"""
Chatbot API Router
Endpoints for Dify Cloud integration
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.config import settings
from app.services.chatbot_service import ChatbotService, ALLOWED_VIEWS
from app.schemas.chatbot import (
    ChatbotQueryRequest,
    ChatbotQueryResponse,
    ChatbotHealthResponse,
    QueryResultResponse
)

router = APIRouter(
    prefix="/chatbot",
    tags=["Chatbot"]
)


def verify_dify_service_key(service_key: Optional[str] = Query(None, alias="service_key")):
    """
    Verify the service key for chatbot endpoints.
    Makes service_key optional but validates if provided.
    For production, make this required.
    """
    if service_key and service_key != settings.DIFY_SERVICE_KEY:
        raise HTTPException(status_code=401, detail="Invalid service key")
    return service_key


@router.get("/health", response_model=ChatbotHealthResponse)
async def chatbot_health():
    """
    Health check endpoint for chatbot service.
    Returns service status and available BI views.
    
    This endpoint can be used by Dify Cloud to verify connectivity.
    """
    return ChatbotHealthResponse(
        status="healthy",
        service="chatbot",
        timestamp=datetime.now().isoformat(),
        available_views=ALLOWED_VIEWS
    )


@router.post("/query", response_model=ChatbotQueryResponse)
async def chatbot_query(
    request: ChatbotQueryRequest,
    service_key: str = Depends(verify_dify_service_key),
    db: Session = Depends(get_db)
):
    """
    Main chatbot query endpoint.
    
    Processes Vietnamese/English finance questions and returns answers
    based on user's financial data.
    
    **Supported question types:**
    - Total expense/income for a period
    - Category breakdown
    - Budget status
    - Wallet balance
    - Recent transactions
    - Monthly trends
    - Daily summary
    
    **Security:**
    - Only queries allowed BI views (no raw SQL)
    - Always filters by user_id
    - Uses predefined query templates
    
    **Example questions (Vietnamese):**
    - "Tổng chi tiêu tháng này là bao nhiêu?"
    - "Chi tiêu theo danh mục"
    - "Kiểm tra ngân sách"
    - "Số dư trong ví"
    - "Giao dịch gần đây"
    
    **Example questions (English):**
    - "What's my total expense this month?"
    - "Show spending by category"
    - "Check my budget status"
    - "What's my wallet balance?"
    - "Recent transactions"
    """
    try:
        service = ChatbotService(db)
        result = service.process_query(
            user_id=request.user_id,
            question=request.question,
            timezone=request.timezone
        )
        
        return ChatbotQueryResponse(
            answer=result["answer"],
            data=result.get("data"),
            suggested_actions=result.get("suggested_actions", [])
        )
        
    except Exception as e:
        # Log error in production
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.post("/query/result", response_model=QueryResultResponse)
async def chatbot_query_result(
    request: ChatbotQueryRequest,
    query_type: str = Query(..., description="Type of query: expense, income, category, budget, wallet, transactions"),
    service_key: str = Depends(verify_dify_service_key),
    db: Session = Depends(get_db)
):
    """
    Returns structured query results (rows) for Dify to format.
    
    This endpoint is useful when Dify wants to format the data
    in its own way rather than receiving pre-formatted answers.
    
    **Query types:**
    - `expense`: Monthly expense data
    - `income`: Monthly income data  
    - `category`: Category breakdown
    - `budget`: Budget vs actual status
    - `wallet`: Wallet balances
    - `transactions`: Recent transactions
    """
    try:
        service = ChatbotService(db)
        time_context = service.extract_time_context(request.question)
        year = time_context["year"]
        month = time_context["month"]
        
        rows = []
        metadata = {"user_id": request.user_id, "year": year, "month": month}
        
        if query_type == "expense" or query_type == "income":
            data = service.query_income_vs_expense(request.user_id, year, month)
            rows = [data]
            
        elif query_type == "category":
            rows = service.query_category_breakdown(request.user_id, year, month)
            
        elif query_type == "budget":
            rows = service.query_budget_status(request.user_id, year, month)
            
        elif query_type == "wallet":
            rows = service.query_wallet_balance(request.user_id)
            metadata = {"user_id": request.user_id}
            
        elif query_type == "transactions":
            rows = service.query_recent_transactions(request.user_id, limit=20)
            metadata = {"user_id": request.user_id, "limit": 20}
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown query_type: {query_type}. Supported: expense, income, category, budget, wallet, transactions"
            )
        
        return QueryResultResponse(
            query_type=query_type,
            rows=rows,
            row_count=len(rows),
            metadata=metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing query: {str(e)}"
        )


@router.get("/views")
async def get_available_views():
    """
    Returns list of available BI views that the chatbot can query.
    This is for transparency and debugging purposes.
    """
    return {
        "allowed_views": ALLOWED_VIEWS,
        "total": len(ALLOWED_VIEWS),
        "note": "Chatbot can only query these predefined views for security"
    }


@router.get("/demo-questions")
async def get_demo_questions():
    """
    Returns a list of demo questions in Vietnamese and English.
    Useful for testing and documentation.
    """
    return {
        "vietnamese": [
            "Tổng chi tiêu tháng này là bao nhiêu?",
            "Thu nhập tháng này của tôi?",
            "Chi tiêu theo danh mục",
            "Kiểm tra ngân sách tháng này",
            "Số dư trong ví là bao nhiêu?",
            "Giao dịch gần đây",
            "Tôi tiết kiệm được bao nhiêu tháng này?",
            "So sánh thu chi tháng trước",
            "Chi tiêu hôm nay",
            "Xu hướng chi tiêu hàng tháng",
            "Có vượt ngân sách không?",
            "Tổng thu nhập năm nay"
        ],
        "english": [
            "What's my total expense this month?",
            "Show my income this month",
            "Spending by category",
            "Check my budget status",
            "What's my wallet balance?",
            "Recent transactions",
            "How much did I save this month?",
            "Compare income and expense last month",
            "Today's spending",
            "Monthly spending trend",
            "Am I over budget?",
            "Total income this year"
        ]
    }
