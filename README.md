# EcommerceFresh API

A robust, feature-rich E-commerce backend API built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**.

## Features

- **Product Management**: Categories, Products, Inventory, Filtering, Pagination.
- **Shopping Cart**: Add/Remove items, Update quantities, Apply discount coupons.
- **Order Processing**: Checkout flow, Order history, Shipping calculation.
- **User Authentication**: JWT-based Secure Registration & Login.
- **Reviews**: Product rating and review system.
- **Advanced Logging**: Structured logging with file rotation.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (via SQLAlchemy ORM)
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: Pydantic
- **Testing**: Pytest

## Prerequisites

- Python 3.9+
- PostgreSQL
- Git

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd EcommerceFresh
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # Activate:
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**:
   - Create a `.env` file in the root directory (copy from `.env.example` if available).
   - Set `DATABASE_URL` (e.g., `postgresql://user:password@localhost:5432/ecommerce_db`).
   - Set `SECRET_KEY` for JWT security.

## Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Testing

Run the integration test suite:

```bash
pytest tests/
```

For verbose output:
```bash
pytest -v tests/
```

## Project Structure

```
├── app/
│   ├── routers/    # API Endpoints (Auth, Cart, Orders, etc.)
│   ├── models.py   # Database Models
│   ├── schemas.py  # Pydantic Schemas
│   ├── main.py     # Application Entry Point
│   └── ...
├── tests/          # Integration Tests
├── logs/           # Application Logs
└── requirements.txt
```
