"""
Summary and analytics routes for dashboard
"""
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/summary", tags=["Summary"])


class MonthlySummary(BaseModel):
    """Monthly summary response"""
    month: int
    year: int
    total_income: Decimal
    total_expense: Decimal
    net_savings: Decimal
    expense_ratio: Decimal
    transaction_count: int


class CategorySummary(BaseModel):
    """Category summary response"""
    category_id: int
    category_name: str
    category_icon: str
    category_color: str
    total_amount: Decimal
    transaction_count: int
    percentage: Decimal


class DashboardSummary(BaseModel):
    """Dashboard summary response"""
    total_balance: Decimal
    total_income_this_month: Decimal
    total_expense_this_month: Decimal
    net_savings_this_month: Decimal
    expense_ratio: Decimal
    transaction_count_this_month: int


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard summary for current month"""
    
    today = datetime.now()
    
    # Get total wallet balance
    balance_query = text("""
        SELECT COALESCE(SUM(balance), 0) as total_balance
        FROM wallets
        WHERE user_id = :user_id AND is_active = TRUE
    """)
    balance_result = db.execute(balance_query, {"user_id": current_user.id}).fetchone()
    total_balance = Decimal(str(balance_result.total_balance or 0))
    
    # Get this month's summary
    summary_query = text("""
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'income' THEN amount END), 0) as total_income,
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount END), 0) as total_expense,
            COUNT(*) as transaction_count
        FROM transactions
        WHERE user_id = :user_id
          AND EXTRACT(YEAR FROM transaction_date) = :year
          AND EXTRACT(MONTH FROM transaction_date) = :month
    """)
    summary_result = db.execute(summary_query, {
        "user_id": current_user.id,
        "year": today.year,
        "month": today.month
    }).fetchone()
    
    total_income = Decimal(str(summary_result.total_income or 0))
    total_expense = Decimal(str(summary_result.total_expense or 0))
    net_savings = total_income - total_expense
    expense_ratio = (total_expense / total_income * 100) if total_income > 0 else Decimal(0)
    
    return DashboardSummary(
        total_balance=total_balance,
        total_income_this_month=total_income,
        total_expense_this_month=total_expense,
        net_savings_this_month=net_savings,
        expense_ratio=round(expense_ratio, 2),
        transaction_count_this_month=summary_result.transaction_count
    )


@router.get("/monthly", response_model=List[MonthlySummary])
async def get_monthly_summary(
    months: int = Query(default=6, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly summary for the last N months"""
    
    query = text("""
        WITH monthly_data AS (
            SELECT 
                EXTRACT(YEAR FROM transaction_date)::INTEGER AS year,
                EXTRACT(MONTH FROM transaction_date)::INTEGER AS month,
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount END), 0) AS total_income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount END), 0) AS total_expense,
                COUNT(*) AS transaction_count
            FROM transactions
            WHERE user_id = :user_id
              AND transaction_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL ':months months'
            GROUP BY 
                EXTRACT(YEAR FROM transaction_date),
                EXTRACT(MONTH FROM transaction_date)
        )
        SELECT 
            year,
            month,
            total_income,
            total_expense,
            total_income - total_expense AS net_savings,
            CASE 
                WHEN total_income > 0 
                THEN ROUND(total_expense * 100.0 / total_income, 2)
                ELSE 0 
            END AS expense_ratio,
            transaction_count
        FROM monthly_data
        ORDER BY year DESC, month DESC
    """.replace(":months", str(months - 1)))
    
    result = db.execute(query, {"user_id": current_user.id})
    
    summaries = []
    for row in result:
        summaries.append(MonthlySummary(
            month=row.month,
            year=row.year,
            total_income=Decimal(str(row.total_income)),
            total_expense=Decimal(str(row.total_expense)),
            net_savings=Decimal(str(row.net_savings)),
            expense_ratio=Decimal(str(row.expense_ratio)),
            transaction_count=row.transaction_count
        ))
    
    return summaries


@router.get("/categories", response_model=List[CategorySummary])
async def get_category_summary(
    type: str = Query(default="expense"),
    month: int = Query(default=datetime.now().month),
    year: int = Query(default=datetime.now().year),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending/income by category for a specific month"""
    
    query = text("""
        SELECT 
            c.id AS category_id,
            c.name AS category_name,
            c.icon AS category_icon,
            c.color AS category_color,
            COALESCE(SUM(t.amount), 0) AS total_amount,
            COUNT(t.id) AS transaction_count,
            ROUND(
                COALESCE(SUM(t.amount), 0) * 100.0 / 
                NULLIF(SUM(SUM(t.amount)) OVER (), 0)
            , 2) AS percentage
        FROM categories c
        LEFT JOIN transactions t ON c.id = t.category_id
            AND t.user_id = :user_id
            AND EXTRACT(YEAR FROM t.transaction_date) = :year
            AND EXTRACT(MONTH FROM t.transaction_date) = :month
        WHERE c.type = :type
          AND c.is_active = TRUE
          AND (c.user_id IS NULL OR c.user_id = :user_id)
        GROUP BY c.id, c.name, c.icon, c.color
        HAVING COALESCE(SUM(t.amount), 0) > 0
        ORDER BY total_amount DESC
    """)
    
    result = db.execute(query, {
        "user_id": current_user.id,
        "type": type,
        "year": year,
        "month": month
    })
    
    summaries = []
    for row in result:
        summaries.append(CategorySummary(
            category_id=row.category_id,
            category_name=row.category_name,
            category_icon=row.category_icon,
            category_color=row.category_color,
            total_amount=Decimal(str(row.total_amount)),
            transaction_count=row.transaction_count,
            percentage=Decimal(str(row.percentage or 0))
        ))
    
    return summaries
