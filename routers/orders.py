from fastapi import APIRouter, HTTPException, status, Depends, Header, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from database import get_db
from models import Order, OrderItem, CartItem, Product, User, Coupon, OrderStatus
from schemas import OrderCreate, OrderResponse, OrderStatusEnum
from routers.auth import get_current_user_from_header

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    order_data: OrderCreate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Convert cart to order, apply coupon, calculate totals, and clear cart"""
    user = get_current_user_from_header(authorization, db)
    
    # Get user's cart items
    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    # Calculate subtotal
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    
    # Apply coupon if provided
    discount_amount = 0.0
    if order_data.coupon_code:
        coupon = db.query(Coupon).filter(
            (Coupon.code == order_data.coupon_code) & (Coupon.is_active == True)
        ).first()
        
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or inactive coupon"
            )
        
        # Check if coupon is expired
        from datetime import datetime
        if coupon.expiry_date and coupon.expiry_date < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coupon has expired"
            )
        
        # Check max uses
        if coupon.max_uses and coupon.current_uses >= coupon.max_uses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coupon usage limit reached"
            )
        
        # Calculate discount
        if coupon.discount_percentage:
            discount_amount = subtotal * (coupon.discount_percentage / 100)
        elif coupon.discount_amount:
            discount_amount = coupon.discount_amount
        
        # Increment coupon usage
        coupon.current_uses += 1
    
    # For now, shipping_cost is calculated as 0 (can be integrated with shipping router)
    shipping_cost = 0.0
    
    # Calculate total
    total_amount = subtotal - discount_amount + shipping_cost
    
    # Create order
    db_order = Order(
        user_id=user.id,
        total_amount=total_amount,
        shipping_address=order_data.shipping_address,
        shipping_cost=shipping_cost,
        discount_amount=discount_amount,
        coupon_code=order_data.coupon_code,
        status=OrderStatus.PENDING
    )
    
    db.add(db_order)
    db.flush()  # Flush to get the order ID
    
    # Create order items from cart items
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=db_order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        db.add(order_item)
    
    # Clear cart
    for cart_item in cart_items:
        db.delete(cart_item)
    
    db.commit()
    db.refresh(db_order)
    
    return db_order

@router.get("/", response_model=List[OrderResponse])
def get_user_orders(
    user_id: int = Query(...),
    authorization: Optional[str] = Header(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get order history for a user"""
    user = get_current_user_from_header(authorization, db)
    
    # Verify ownership
    if user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these orders"
        )
    
    orders = db.query(Order).filter(
        Order.user_id == user_id
    ).offset(skip).limit(limit).all()
    
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get order details by ID"""
    user = get_current_user_from_header(authorization, db)
    
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify ownership
    if order.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order

@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    new_status: OrderStatusEnum,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Update order status (admin only - in production)"""
    # In production, add admin check here
    
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order.status = new_status
    db.commit()
    db.refresh(order)
    
    return order
