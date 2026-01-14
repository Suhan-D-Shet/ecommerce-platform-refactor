from fastapi import APIRouter, HTTPException, status, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database import get_db
from models import Coupon
from schemas import CouponCreate, CouponResponse
from routers.auth import get_current_user_from_header

router = APIRouter(prefix="/coupons", tags=["Coupons"])

@router.post("/", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(
    coupon_data: CouponCreate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Create a new coupon (admin only in production)"""
    # In production, verify admin role here
    
    # Check if coupon already exists
    existing_coupon = db.query(Coupon).filter(Coupon.code == coupon_data.code).first()
    if existing_coupon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon code already exists"
        )
    
    # Validate discount (must have either percentage or amount)
    if not coupon_data.discount_percentage and not coupon_data.discount_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either discount_percentage or discount_amount"
        )
    
    db_coupon = Coupon(
        code=coupon_data.code,
        discount_percentage=coupon_data.discount_percentage,
        discount_amount=coupon_data.discount_amount,
        max_uses=coupon_data.max_uses,
        expiry_date=coupon_data.expiry_date
    )
    
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    
    return db_coupon

@router.post("/validate", response_model=CouponResponse)
def validate_coupon(
    code: str,
    db: Session = Depends(get_db)
):
    """Validate a coupon code"""
    coupon = db.query(Coupon).filter(Coupon.code == code).first()
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    if not coupon.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon is inactive"
        )
    
    if coupon.expiry_date and coupon.expiry_date < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon has expired"
        )
    
    if coupon.max_uses and coupon.current_uses >= coupon.max_uses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon usage limit reached"
        )
    
    return coupon

@router.get("/{coupon_id}", response_model=CouponResponse)
def get_coupon(
    coupon_id: int,
    db: Session = Depends(get_db)
):
    """Get coupon details"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    return coupon
