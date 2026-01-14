from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from routers import auth, products, categories, cart, orders, reviews, coupons, shipping
from middleware import LoggingMiddleware
from database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    logging.info("Application startup")
    yield
    logging.info("Application shutdown")

app = FastAPI(
    title="E-Commerce API",
    description="Complete e-commerce platform with products, cart, orders, and reviews",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(reviews.router)
app.include_router(coupons.router)
app.include_router(shipping.router)

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "E-Commerce API is running",
        "docs": "/docs",
        "health": "OK"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
