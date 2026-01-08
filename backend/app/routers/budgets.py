"""
Budget routes
"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models.user import User
from app.models.category import Category
from app.models.budget import Budget
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetStatus
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/budgets", tags=["Budgets"])


def budget_to_response(budget: Budget) -> BudgetResponse:
    """Convert budget model to response with related data"""
    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        category_id=budget.category_id,
        amount=budget.amount,
        month=budget.month,
        year=budget.year,
        created_at=budget.created_at,
        category_name=budget.category.name if budget.category else None,
        category_icon=budget.category.icon if budget.category else None,
        category_color=budget.category.color if budget.category else None
    )


@router.get("/", response_model=List[BudgetResponse])
async def get_budgets(
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budgets for current user"""
    
    query = db.query(Budget).filter(Budget.user_id == current_user.id)
    
    if month:
        query = query.filter(Budget.month == month)
    if year:
        query = query.filter(Budget.year == year)
    
    budgets = query.all()
    return [budget_to_response(b) for b in budgets]


@router.get("/status", response_model=List[BudgetStatus])
async def get_budget_status(
    month: int = Query(default=datetime.now().month),
    year: int = Query(default=datetime.now().year),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budget status with actual spending"""
    
    query = text("""
        SELECT 
            b.id,
            b.category_id,
            c.name AS category_name,
            c.icon AS category_icon,
            c.color AS category_color,
            b.amount AS budget_amount,
            COALESCE(actual.spent, 0) AS actual_spent,
            b.amount - COALESCE(actual.spent, 0) AS remaining,
            ROUND(COALESCE(actual.spent, 0) * 100.0 / NULLIF(b.amount, 0), 2) AS usage_percentage,
            CASE 
                WHEN COALESCE(actual.spent, 0) >= b.amount THEN 'exceeded'
                WHEN COALESCE(actual.spent, 0) >= b.amount * 0.8 THEN 'warning'
                ELSE 'safe'
            END AS status,
            b.month,
            b.year
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        LEFT JOIN (
            SELECT 
                user_id,
                category_id,
                EXTRACT(YEAR FROM transaction_date)::INTEGER AS year,
                EXTRACT(MONTH FROM transaction_date)::INTEGER AS month,
                SUM(amount) AS spent
            FROM transactions
            WHERE type = 'expense'
            GROUP BY user_id, category_id, 
                EXTRACT(YEAR FROM transaction_date),
                EXTRACT(MONTH FROM transaction_date)
        ) actual ON b.user_id = actual.user_id 
            AND b.category_id = actual.category_id 
            AND b.year = actual.year 
            AND b.month = actual.month
        WHERE b.user_id = :user_id
          AND b.year = :year
          AND b.month = :month
        ORDER BY usage_percentage DESC NULLS LAST
    """)
    
    result = db.execute(query, {
        "user_id": current_user.id,
        "year": year,
        "month": month
    })
    
    budget_statuses = []
    for row in result:
        budget_statuses.append(BudgetStatus(
            id=row.id,
            category_id=row.category_id,
            category_name=row.category_name,
            category_icon=row.category_icon,
            category_color=row.category_color,
            budget_amount=Decimal(str(row.budget_amount)),
            actual_spent=Decimal(str(row.actual_spent)),
            remaining=Decimal(str(row.remaining)),
            usage_percentage=Decimal(str(row.usage_percentage or 0)),
            status=row.status,
            month=row.month,
            year=row.year
        ))
    
    return budget_statuses


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new budget"""
    
    # Verify category exists and is expense type
    category = db.query(Category).filter(
        Category.id == budget_data.category_id,
        Category.type == "expense",
        Category.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found or not an expense category"
        )
    
    # Check if budget already exists
    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category_id == budget_data.category_id,
        Budget.month == budget_data.month,
        Budget.year == budget_data.year
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget for this category and month already exists"
        )
    
    new_budget = Budget(
        user_id=current_user.id,
        category_id=budget_data.category_id,
        amount=budget_data.amount,
        month=budget_data.month,
        year=budget_data.year
    )
    
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    
    return budget_to_response(new_budget)


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a budget"""
    
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    if budget_data.amount is not None:
        budget.amount = budget_data.amount
    
    db.commit()
    db.refresh(budget)
    
    return budget_to_response(budget)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a budget"""
    
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    db.delete(budget)
    db.commit()
    
    return None
