"""
Seed script to populate database with sample data
Run with: python scripts/seed_data.py
"""

import sys
sys.path.insert(0, '.')

from database import SessionLocal, engine, Base
from models import Category, Product, Coupon, User
from utils import hash_password
from datetime import datetime, timedelta

# Create tables
Base.metadata.create_all(bind=engine)

def seed_data():
    """Populate database with sample data"""
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(Product).delete()
        db.query(Category).delete()
        db.query(Coupon).delete()
        db.query(User).delete()
        
        # Create categories
        categories = [
            Category(name="Electronics", description="Electronic devices and gadgets"),
            Category(name="Clothing", description="Apparel and fashion items"),
            Category(name="Books", description="Physical and digital books"),
            Category(name="Home & Garden", description="Home and garden items"),
        ]
        db.add_all(categories)
        db.flush()
        
        # Create products
        products = [
            Product(
                name="Wireless Headphones",
                description="High-quality wireless headphones with noise cancellation",
                price=79.99,
                stock=50,
                weight=0.25,
                category_id=categories[0].id
            ),
            Product(
                name="USB-C Cable",
                description="Durable USB-C charging cable, 2 meters long",
                price=12.99,
                stock=200,
                weight=0.05,
                category_id=categories[0].id
            ),
            Product(
                name="Cotton T-Shirt",
                description="Comfortable 100% cotton t-shirt",
                price=19.99,
                stock=100,
                weight=0.2,
                category_id=categories[1].id
            ),
            Product(
                name="Running Shoes",
                description="Professional running shoes with cushioning",
                price=119.99,
                stock=30,
                weight=0.5,
                category_id=categories[1].id
            ),
            Product(
                name="Python Programming Book",
                description="Complete guide to Python programming",
                price=34.99,
                stock=45,
                weight=0.8,
                category_id=categories[2].id
            ),
            Product(
                name="Indoor Plant Pot",
                description="Ceramic pot for indoor plants, 20cm diameter",
                price=24.99,
                stock=75,
                weight=1.2,
                category_id=categories[3].id
            ),
        ]
        db.add_all(products)
        db.flush()
        
        # Create coupons
        coupons = [
            Coupon(
                code="SUMMER20",
                discount_percentage=20.0,
                max_uses=100,
                is_active=True,
                expiry_date=datetime.utcnow() + timedelta(days=30)
            ),
            Coupon(
                code="FREESHIP",
                discount_amount=5.0,
                max_uses=50,
                is_active=True,
                expiry_date=datetime.utcnow() + timedelta(days=15)
            ),
            Coupon(
                code="WELCOME10",
                discount_percentage=10.0,
                max_uses=None,
                is_active=True,
                expiry_date=None
            ),
        ]
        db.add_all(coupons)
        db.flush()
        
        # Create test users
        users = [
            User(
                email="user@example.com",
                username="testuser",
                hashed_password=hash_password("password123")
            ),
            User(
                email="john@example.com",
                username="john_doe",
                hashed_password=hash_password("john123")
            ),
        ]
        db.add_all(users)
        
        db.commit()
        print("Database seeded successfully!")
        print(f"Created {len(categories)} categories")
        print(f"Created {len(products)} products")
        print(f"Created {len(coupons)} coupons")
        print(f"Created {len(users)} test users")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
