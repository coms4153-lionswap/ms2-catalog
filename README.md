# Catalog Service

A simple FastAPI service for managing catalog items.

## Features

- CRUD operations for catalog items
- RESTful API endpoints
- Automatic API documentation with Swagger UI
- Pydantic models for data validation
- Health check endpoint

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /items` - Get all items
- `GET /items/{item_id}` - Get item by ID
- `POST /items` - Create new item
- `PUT /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item
- `GET /items/category/{category}` - Get items by category

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

3. Access the API:
- API: http://localhost:8000
- Interactive API docs (Swagger UI): http://localhost:8000/docs
- Alternative API docs (ReDoc): http://localhost:8000/redoc

## Example Usage

### Create an item
```bash
curl -X POST "http://localhost:8000/items" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Laptop",
       "description": "High-performance laptop",
       "price": 999.99,
       "category": "Electronics"
     }'
```

### Get all items
```bash
curl -X GET "http://localhost:8000/items"
```

### Get item by ID
```bash
curl -X GET "http://localhost:8000/items/1"
```

## Data Model

```python
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    category: str
```