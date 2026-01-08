"""
Transaction routes
"""
from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


def transaction_to_response(transaction: Transaction) -> TransactionResponse:
    """Convert transaction model to response with related data"""
    return TransactionResponse(
        id=transaction.id,
        user_id=transaction.user_id,
        wallet_id=transaction.wallet_id,
        category_id=transaction.category_id,
        type=transaction.type,
        amount=transaction.amount,
        description=transaction.description,
        transaction_date=transaction.transaction_date,
        created_at=transaction.created_at,
        category_name=transaction.category.name if transaction.category else None,
        category_icon=transaction.category.icon if transaction.category else None,
        category_color=transaction.category.color if transaction.category else None,
        wallet_name=transaction.wallet.name if transaction.wallet else None
    )


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    type: Optional[str] = None,
    category_id: Optional[int] = None,
    wallet_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions with filters"""
    
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    )
    
    if type:
        query = query.filter(Transaction.type == type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if wallet_id:
        query = query.filter(Transaction.wallet_id == wallet_id)
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    
    transactions = query.order_by(
        desc(Transaction.transaction_date),
        desc(Transaction.created_at)
    ).offset(offset).limit(limit).all()
    
    return [transaction_to_response(t) for t in transactions]


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific transaction"""
    
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction_to_response(transaction)


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    
    # Verify wallet belongs to user
    wallet = db.query(Wallet).filter(
        Wallet.id == transaction_data.wallet_id,
        Wallet.user_id == current_user.id,
        Wallet.is_active == True
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet not found"
        )
    
    # Verify category exists and is accessible
    category = db.query(Category).filter(
        Category.id == transaction_data.category_id,
        Category.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found"
        )
    
    # Verify category type matches transaction type
    if category.type != transaction_data.type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category type ({category.type}) doesn't match transaction type ({transaction_data.type})"
        )
    
    new_transaction = Transaction(
        user_id=current_user.id,
        wallet_id=transaction_data.wallet_id,
        category_id=transaction_data.category_id,
        type=transaction_data.type,
        amount=transaction_data.amount,
        description=transaction_data.description,
        transaction_date=transaction_data.transaction_date
    )
    
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return transaction_to_response(new_transaction)


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a transaction"""
    
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Verify new wallet if provided
    if transaction_data.wallet_id is not None:
        wallet = db.query(Wallet).filter(
            Wallet.id == transaction_data.wallet_id,
            Wallet.user_id == current_user.id,
            Wallet.is_active == True
        ).first()
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wallet not found"
            )
        transaction.wallet_id = transaction_data.wallet_id
    
    # Verify new category if provided
    if transaction_data.category_id is not None:
        category = db.query(Category).filter(
            Category.id == transaction_data.category_id,
            Category.is_active == True
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )
        transaction.category_id = transaction_data.category_id
    
    if transaction_data.type is not None:
        transaction.type = transaction_data.type
    if transaction_data.amount is not None:
        transaction.amount = transaction_data.amount
    if transaction_data.description is not None:
        transaction.description = transaction_data.description
    if transaction_data.transaction_date is not None:
        transaction.transaction_date = transaction_data.transaction_date
    
    db.commit()
    db.refresh(transaction)
    
    return transaction_to_response(transaction)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a transaction"""
    
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    db.delete(transaction)
    db.commit()
    
    return None
