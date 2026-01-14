# Run and Test Instructions

## Prerequisites
- Python 3.9+
- PostgreSQL (or configure database in `.env`)
- Virtual Environment (recommended)

## Installation
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application
To start the FastAPI server with hot-reloading enabled:

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: `http://127.0.0.1:8000`
- **Documentation (Swagger UI)**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## Testing
The project includes integration tests located in the `tests/` directory.

To run the tests:

```bash
pytest tests/
```

To run with verbose output:

```bash
pytest -v tests/
```
