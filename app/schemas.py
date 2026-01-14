from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum

# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Category Schemas
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Product Schemas
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    weight: float = Field(default=0.0, ge=0)
    category_id: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    weight: Optional[float] = None
    category_id: Optional[int] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    weight: float
    category_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Cart Schemas
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total: float

# Review Schemas
class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Order Schemas
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    
    class Config:
        from_attributes = True

class OrderStatusEnum(str, PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderCreate(BaseModel):
    shipping_address: str
    coupon_code: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    shipping_address: str
    shipping_cost: float
    discount_amount: float
    coupon_code: Optional[str]
    status: str
    items: List[OrderItemResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Coupon Schemas
class CouponCreate(BaseModel):
    code: str = Field(..., max_length=50)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    discount_amount: Optional[float] = Field(None, ge=0)
    max_uses: Optional[int] = None
    expiry_date: Optional[datetime] = None

class CouponResponse(BaseModel):
    id: int
    code: str
    discount_percentage: Optional[float]
    discount_amount: Optional[float]
    is_active: bool
    current_uses: int
    
    class Config:
        from_attributes = True

# Shipping Schemas
class ShippingCalculateRequest(BaseModel):
    address: str
    total_weight: float
    total_amount: float

class ShippingCalculateResponse(BaseModel):
    shipping_cost: float
    estimated_days: int
    method: str
