"""
Wallet routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.wallet import WalletCreate, WalletUpdate, WalletResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/wallets", tags=["Wallets"])


@router.get("/", response_model=List[WalletResponse])
async def get_wallets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all wallets for current user"""
    
    wallets = db.query(Wallet).filter(
        Wallet.user_id == current_user.id,
        Wallet.is_active == True
    ).order_by(Wallet.created_at).all()
    
    return wallets


@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(
    wallet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific wallet"""
    
    wallet = db.query(Wallet).filter(
        Wallet.id == wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    return wallet


@router.post("/", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(
    wallet_data: WalletCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new wallet"""
    
    # Check if wallet with same name exists
    existing = db.query(Wallet).filter(
        Wallet.user_id == current_user.id,
        Wallet.name == wallet_data.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet with this name already exists"
        )
    
    new_wallet = Wallet(
        user_id=current_user.id,
        name=wallet_data.name,
        balance=wallet_data.initial_balance,
        currency=wallet_data.currency,
        icon=wallet_data.icon
    )
    
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    
    return new_wallet


@router.put("/{wallet_id}", response_model=WalletResponse)
async def update_wallet(
    wallet_id: int,
    wallet_data: WalletUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a wallet"""
    
    wallet = db.query(Wallet).filter(
        Wallet.id == wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    if wallet_data.name is not None:
        # Check for duplicate name
        existing = db.query(Wallet).filter(
            Wallet.user_id == current_user.id,
            Wallet.name == wallet_data.name,
            Wallet.id != wallet_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wallet with this name already exists"
            )
        wallet.name = wallet_data.name
    
    if wallet_data.icon is not None:
        wallet.icon = wallet_data.icon
    if wallet_data.is_active is not None:
        wallet.is_active = wallet_data.is_active
    
    db.commit()
    db.refresh(wallet)
    
    return wallet


@router.delete("/{wallet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wallet(
    wallet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a wallet (soft delete)"""
    
    wallet = db.query(Wallet).filter(
        Wallet.id == wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    wallet.is_active = False
    db.commit()
    
    return None
