from fastapi import APIRouter, HTTPException, status, Depends, Header, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import CartItem, Product, User
from app.schemas import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse
from app.routers.auth import get_current_user_from_header

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/", response_model=CartResponse)
def get_cart(
    user_id: int = Query(...),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get user's cart with all items and total"""
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Fetch cart items
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    
    # Calculate total
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    return {
        "items": cart_items,
        "total": total
    }

@router.post("/", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    cart_data: CartItemCreate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Add item to cart or update quantity if exists"""
    # Get current user from header
    user = get_current_user_from_header(authorization, db)
    
    # Verify product exists
    product = db.query(Product).filter(Product.id == cart_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if item already in cart
    cart_item = db.query(CartItem).filter(
        (CartItem.user_id == user.id) & (CartItem.product_id == cart_data.product_id)
    ).first()
    
    if cart_item:
        # Update quantity
        cart_item.quantity += cart_data.quantity
    else:
        # Create new cart item
        cart_item = CartItem(
            user_id=user.id,
            product_id=cart_data.product_id,
            quantity=cart_data.quantity
        )
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart_item)
    
    return cart_item

@router.put("/{cart_item_id}", response_model=CartItemResponse)
def update_cart_item(
    cart_item_id: int,
    update_data: CartItemUpdate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    user = get_current_user_from_header(authorization, db)
    
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Verify ownership
    if cart_item.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this cart item"
        )
    
    cart_item.quantity = update_data.quantity
    db.commit()
    db.refresh(cart_item)
    
    return cart_item

@router.delete("/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    cart_item_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    user = get_current_user_from_header(authorization, db)
    
    cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Verify ownership
    if cart_item.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this cart item"
        )
    
    db.delete(cart_item)
    db.commit()

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    user_id: int = Query(...),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Clear all items from user's cart"""
    user = get_current_user_from_header(authorization, db)
    
    # Verify ownership
    if user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to clear this cart"
        )
    
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
