"""
Automation API endpoints for n8n workflows
These endpoints provide data for automated notifications and alerts
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime, date
import calendar

from app.database import get_db
from app.config import settings

router = APIRouter(
    prefix="/api/automation",
    tags=["Automation"]
)


def verify_service_key(service_key: str = Query(..., alias="service_key")):
    """Verify the service key for automation endpoints"""
    if service_key != settings.N8N_SERVICE_KEY:
        raise HTTPException(status_code=401, detail="Invalid service key")
    return service_key


@router.get("/bills/upcoming")
async def get_upcoming_bills(
    month: str = Query(..., description="Month in YYYY-MM format"),
    service_key: str = Depends(verify_service_key),
    db: Session = Depends(get_db)
):
    """
    Get upcoming bills for a specific month.
    Used by n8n Monthly Bill Reminder workflow.
    
    Args:
        month: Month in YYYY-MM format (e.g., "2026-01")
        service_key: Service authentication key
    
    Returns:
        List of upcoming bills grouped by user
    """
    try:
        # Parse month
        year, month_num = map(int, month.split("-"))
        
        # Get last day of month
        _, last_day = calendar.monthrange(year, month_num)
        
        # Query upcoming bills
        query = text("""
            SELECT 
                b.id AS bill_id,
                b.user_id,
                u.email AS user_email,
                u.full_name AS user_name,
                b.name AS bill_name,
                b.amount,
                b.due_day,
                b.description,
                w.name AS wallet_name,
                w.currency,
                c.name AS category_name
            FROM bills b
            JOIN users u ON b.user_id = u.id
            JOIN wallets w ON b.wallet_id = w.id
            JOIN categories c ON b.category_id = c.id
            WHERE b.is_active = TRUE
            ORDER BY b.user_id, b.due_day
        """)
        
        result = db.execute(query)
        rows = result.fetchall()
        
        bills = []
        for row in rows:
            # Calculate actual due date (handle months with fewer days)
            actual_due_day = min(row.due_day, last_day)
            due_date = date(year, month_num, actual_due_day)
            
            bills.append({
                "bill_id": row.bill_id,
                "user_id": row.user_id,
                "user_email": row.user_email,
                "user_name": row.user_name,
                "bill_name": row.bill_name,
                "amount": float(row.amount),
                "due_day": row.due_day,
                "due_date": due_date.strftime("%Y-%m-%d"),
                "description": row.description,
                "wallet_name": row.wallet_name,
                "currency": row.currency,
                "category_name": row.category_name,
                "month": month
            })
        
        return {
            "month": month,
            "total_bills": len(bills),
            "bills": bills
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid month format. Use YYYY-MM")


@router.get("/budget/overruns")
async def get_budget_overruns(
    year: Optional[int] = Query(None, description="Year (default: current year)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month 1-12 (default: current month)"),
    service_key: str = Depends(verify_service_key),
    db: Session = Depends(get_db)
):
    """
    Get budget overruns for alerts.
    Used by n8n Budget Overrun Alert workflow.
    
    Args:
        year: Year (default: current)
        month: Month 1-12 (default: current)
        service_key: Service authentication key
    
    Returns:
        List of budget overruns grouped by user
    """
    now = datetime.now()
    target_year = year or now.year
    target_month = month or now.month
    
    period = f"{target_year}-{target_month:02d}"
    
    query = text("""
        SELECT 
            bva.user_id,
            u.email AS user_email,
            u.full_name AS user_name,
            bva.year,
            bva.month,
            bva.category_id,
            bva.category_name,
            bva.category_color,
            bva.budget_amount,
            bva.actual_spent,
            bva.actual_spent - bva.budget_amount AS overrun_amount,
            bva.usage_percentage,
            bva.status
        FROM v_budget_vs_actual bva
        JOIN users u ON bva.user_id = u.id
        WHERE bva.year = :year 
          AND bva.month = :month
          AND bva.actual_spent > bva.budget_amount
        ORDER BY bva.user_id, bva.actual_spent - bva.budget_amount DESC
    """)
    
    result = db.execute(query, {"year": target_year, "month": target_month})
    rows = result.fetchall()
    
    overruns = []
    for row in rows:
        overruns.append({
            "user_id": row.user_id,
            "user_email": row.user_email,
            "user_name": row.user_name,
            "period": period,
            "year": row.year,
            "month": row.month,
            "category_id": row.category_id,
            "category_name": row.category_name,
            "budget_amount": float(row.budget_amount),
            "actual_spent": float(row.actual_spent),
            "overrun_amount": float(row.overrun_amount),
            "usage_percentage": float(row.usage_percentage) if row.usage_percentage else 0
        })
    
    return {
        "period": period,
        "total_overruns": len(overruns),
        "overruns": overruns
    }


@router.get("/health")
async def automation_health():
    """Health check endpoint for automation service"""
    return {
        "status": "healthy",
        "service": "automation",
        "timestamp": datetime.now().isoformat()
    }
