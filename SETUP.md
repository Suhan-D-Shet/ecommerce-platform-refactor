# E-Commerce API Setup Guide

## Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip

## Installation Steps

### 1. Clone and Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database
Create a `.env` file based on `.env.example`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce_db
SECRET_KEY=your-secure-random-key
DEBUG=True
```

### 4. Create Database
```bash
# Using psql
createdb ecommerce_db
```

### 5. Run the Server
```bash
python main.py
```

The API will be available at `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Structure
See models.py for complete schema definition.

## API Endpoints
All endpoints are documented in the Swagger UI.
