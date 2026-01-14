import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.utils import hash_password

# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_check(db):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["health"] == "OK"

def test_register_user(db):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"

def test_login_user(db):
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    return data["access_token"]

def test_create_category(db):
    token = test_login_user(db)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/categories/",
        json={"name": "Test Category", "description": "Testing"},
        headers=headers
    )
    # Note: Authorization is not strictly required for categories in current impl, but good practice
    # Actually categories POST doesn't enforce auth in code we read? 
    # Let's check categories.py: def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    # No auth dependency. 
    # But it returns 201.
    if response.status_code == 400: # Already exists?
        assert response.json()["detail"] == "Category with this name already exists"
    else:
        assert response.status_code == 201
        assert response.json()["name"] == "Test Category"

def test_create_product(db):
    # Ensure category exists
    client.post("/categories/", json={"name": "Electronics"})
    
    # Get Category ID (assuming it's 1 or 2)
    cats = client.get("/categories/").json()
    cat_id = cats[0]["id"]
    
    response = client.post(
        "/products/",
        json={
            "name": "Test Phone", 
            "price": 100.0, 
            "category_id": cat_id,
            "stock": 10
        }
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Phone"
    return response.json()["id"]

def test_coupon_flow(db):
    token = test_login_user(db)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create Coupon (requires direct DB insert as admin endpoint is hypothetical or unprotected?)
    # coupons.py has POST / but logic says "admin only in production". Currently unprotected.
    response = client.post(
        "/coupons/",
        json={
            "code": "SAVE10",
            "discount_percentage": 10.0,
            "max_uses": 100
        }
    )
    assert response.status_code == 201
    
    # 2. Add item to cart
    prod_id = test_create_product(db)
    client.post(
        "/cart/",
        json={"product_id": prod_id, "quantity": 1},
        headers=headers
    )
    
    # 3. Get User ID
    user_resp = client.get("/auth/me", headers=headers)
    user_id = user_resp.json()["id"]
    
    # 4. Apply Coupon
    response = client.post(
        "/cart/apply-coupon",
        json={"user_id": user_id, "coupon_code": "SAVE10"},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Coupon applied"
    assert data["discount"] == 10.0 # 10% of 100
    assert data["new_total"] == 90.0

def test_apply_invalid_coupon(db):
    token = test_login_user(db)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get User ID
    user_resp = client.get("/auth/me", headers=headers)
    user_id = user_resp.json()["id"]
    
    response = client.post(
        "/cart/apply-coupon",
        json={"user_id": user_id, "coupon_code": "INVALID"},
        headers=headers
    )
    
    assert response.status_code == 404


def test_reviews_flow(db):
    token = test_login_user(db)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Ensure product exists and get ID
    prod_id = test_create_product(db)
    
    # 1. Add Review
    response = client.post(
        f"/products/{prod_id}/reviews",
        json={"rating": 5, "comment": "Great!"},
        headers=headers
    )
    assert response.status_code == 201
    assert response.json()["rating"] == 5
    
    # 2. Get Reviews
    response = client.get(f"/products/{prod_id}/reviews")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["comment"] == "Great!"


def test_checkout_and_orders(db):
    # Create a fresh user for this test to ensure empty cart
    client.post(
        "/auth/register",
        json={
            "email": "checkout@example.com",
            "username": "checkoutuser",
            "password": "password123"
        }
    )
    # Login
    response = client.post(
        "/auth/login",
        json={
            "email": "checkout@example.com",
            "password": "password123"
        }
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Setup: Add to cart
    prod_id = test_create_product(db)
    client.post(
        "/cart/",
        json={"product_id": prod_id, "quantity": 2}, # 2 * 100 = 200
        headers=headers
    )
    
    # 2. Checkout
    response = client.post(
        "/orders/checkout",
        json={
            "shipping_address": "123 Test St",
            "coupon_code": None
        },
        headers=headers
    )
    assert response.status_code == 201
    order_data = response.json()
    assert order_data["total_amount"] == 200.0
    assert order_data["status"] == "pending"
    order_id = order_data["id"]
    
    # 3. Get User Orders
    user_resp = client.get("/auth/me", headers=headers)
    user_id = user_resp.json()["id"]
    
    response = client.get(f"/orders/?user_id={user_id}", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    
    # 4. Get Specific Order
    response = client.get(f"/orders/{order_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_shipping_calculation(db):
    response = client.post(
        "/shipping/calculate",
        json={
            "address": "Test Address",
            "total_weight": 5.0,
            "total_amount": 50.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    # 5kg * $2 + $5 base = $15
    assert data["shipping_cost"] == 15.0 
    
    # Free shipping test (>100)
    response = client.post(
        "/shipping/calculate",
        json={
            "address": "Test Address",
            "total_weight": 5.0,
            "total_amount": 150.0
        }
    )
    assert response.json()["shipping_cost"] == 0.0

