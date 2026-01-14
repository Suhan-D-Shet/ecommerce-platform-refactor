from fastapi import APIRouter, HTTPException, status
from schemas import ShippingCalculateRequest, ShippingCalculateResponse

router = APIRouter(prefix="/shipping", tags=["Shipping"])

def calculate_shipping_cost(weight: float, total_amount: float) -> tuple[float, int]:
    """
    Calculate shipping cost and estimated delivery days based on weight and total amount
    
    Rules:
    - Base cost: $5.00
    - Per kg: $2.00
    - Free shipping for orders over $100
    - Estimated delivery: 3-5 days standard
    """
    base_cost = 5.0
    cost_per_kg = 2.0
    
    # Calculate weight-based cost
    weight_cost = weight * cost_per_kg
    shipping_cost = base_cost + weight_cost
    
    # Free shipping for orders over $100
    if total_amount >= 100:
        shipping_cost = 0.0
    
    # Estimate delivery days
    estimated_days = 3 if shipping_cost == 0 else 5
    
    return shipping_cost, estimated_days

@router.post("/calculate", response_model=ShippingCalculateResponse)
def calculate_shipping(request: ShippingCalculateRequest):
    """Calculate shipping cost based on address and weight"""
    if request.total_weight < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Weight cannot be negative"
        )
    
    shipping_cost, estimated_days = calculate_shipping_cost(
        request.total_weight,
        request.total_amount
    )
    
    return {
        "shipping_cost": shipping_cost,
        "estimated_days": estimated_days,
        "method": "Standard Shipping"
    }
