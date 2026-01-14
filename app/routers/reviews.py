from fastapi import APIRouter, HTTPException, status, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Review, Product, User
from schemas import ReviewCreate, ReviewResponse
from routers.auth import get_current_user_from_header

router = APIRouter(prefix="/products", tags=["Reviews"])

@router.post("/{product_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    product_id: int,
    review_data: ReviewCreate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Submit a review for a product"""
    user = get_current_user_from_header(authorization, db)
    
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user already reviewed this product
    existing_review = db.query(Review).filter(
        (Review.product_id == product_id) & (Review.user_id == user.id)
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product"
        )
    
    # Create review
    db_review = Review(
        product_id=product_id,
        user_id=user.id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    return db_review

@router.get("/{product_id}/reviews")
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    """Get all reviews for a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    return reviews

@router.put("/{product_id}/reviews/{review_id}", response_model=ReviewResponse)
def update_review(
    product_id: int,
    review_id: int,
    review_data: ReviewCreate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Update a review (user can only update their own)"""
    user = get_current_user_from_header(authorization, db)
    
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Verify ownership
    if review.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this review"
        )
    
    review.rating = review_data.rating
    review.comment = review_data.comment
    
    db.commit()
    db.refresh(review)
    
    return review

@router.delete("/{product_id}/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    product_id: int,
    review_id: int,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Delete a review (user can only delete their own)"""
    user = get_current_user_from_header(authorization, db)
    
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Verify ownership
    if review.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this review"
        )
    
    db.delete(review)
    db.commit()
