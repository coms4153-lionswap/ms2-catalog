from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import uvicorn

from models.item import Item, ItemCreate, ItemUpdate, ItemStatus
from models.item_image import ItemImage, ItemImageCreate, ItemImageUpdate

# Create FastAPI instance
app = FastAPI(
    title="Catalog Service API",
    description="Microservice for managing catalog items and item images",
    version="1.0.0",
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
items_db = []
item_images_db = []
next_item_id = 1
next_image_id = 1

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Catalog Service API"}

# ===== ITEM ENDPOINTS =====

# Get all items with optional filtering and pagination
@app.get("/items", response_model=List[Item], tags=["Items"])
async def get_items(
    category: Optional[str] = Query(None, description="Filter by item category"),
    status: Optional[ItemStatus] = Query(None, description="Filter by item status"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum item price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum item price"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip from the start"),
):
    """
    Get catalog items with optional filtering and pagination.

    Supported query parameters:
    - category: filter items by category (case-insensitive)
    - status: filter items by status
    - min_price / max_price: filter items by price range
    - limit: max number of items to return (default 50, max 100)
    - offset: number of items to skip (for pagination)
    """
    filtered_items = items_db

    # Filter by category
    if category is not None:
        filtered_items = [
            item for item in filtered_items
            if item.category is not None and item.category.lower() == category.lower()
        ]

    # Filter by status
    if status is not None:
        filtered_items = [item for item in filtered_items if item.status == status]

    # Filter by price range
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price is not None and item.price >= min_price]

    if max_price is not None:
        filtered_items = [item for item in filtered_items if item.price is not None and item.price <= max_price]

    # Apply pagination
    start = offset
    end = offset + limit
    return filtered_items[start:end]

# Get item by ID
@app.get("/items/{item_id}", response_model=Item, tags=["Items"])
async def get_item(item_id: int):
    """Get a specific item by ID"""
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# Create new item
@app.post("/items", response_model=Item, tags=["Items"])
async def create_item(item: ItemCreate):
    """Create a new catalog item"""
    global next_item_id
    now = datetime.now()
    new_item = Item(
        id=next_item_id,
        name=item.name,
        description=item.description,
        price=item.price,
        category=item.category,
        status=item.status,
        created_at=now,
        updated_at=now
    )
    items_db.append(new_item)
    next_item_id += 1
    return new_item

# Update item
@app.put("/items/{item_id}", response_model=Item, tags=["Items"])
async def update_item(item_id: int, item_update: ItemUpdate):
    """Update an existing item"""
    for i, existing_item in enumerate(items_db):
        if existing_item.id == item_id:
            # Update only provided fields
            update_data = item_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing_item, field, value)
            existing_item.updated_at = datetime.now()
            return existing_item
    raise HTTPException(status_code=404, detail="Item not found")

# Delete item
@app.delete("/items/{item_id}", tags=["Items"])
async def delete_item(item_id: int):
    """Delete an item and all its associated images"""
    for i, item in enumerate(items_db):
        if item.id == item_id:
            # Also delete associated images
            item_images_db[:] = [img for img in item_images_db if img.item_id != item_id]
            deleted_item = items_db.pop(i)
            return {"message": f"Item '{deleted_item.name}' and its images deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

# Get items by category
@app.get("/items/category/{category}", response_model=List[Item], tags=["Items"])
async def get_items_by_category(category: str):
    """Get all items in a specific category"""
    return [item for item in items_db if item.category.lower() == category.lower()]

# Get items by status
@app.get("/items/status/{status}", response_model=List[Item], tags=["Items"])
async def get_items_by_status(status: ItemStatus):
    """Get all items with a specific status"""
    return [item for item in items_db if item.status == status]

# ===== ITEM IMAGES ENDPOINTS =====

# Get all images for an item with optional filtering and pagination
@app.get("/items/{item_id}/images", response_model=List[ItemImage], tags=["Item Images"])
async def get_item_images(
    item_id: int,
    is_primary: Optional[bool] = Query(None, description="Filter to only primary or non-primary images"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of images to return"),
    offset: int = Query(0, ge=0, description="Number of images to skip from the start"),
):
    """
    Get images for a specific item with optional filtering and pagination.

    Supported query parameters:
    - is_primary: filter images by whether they are marked as primary
    - limit: max number of images to return (default 50, max 100)
    - offset: number of images to skip (for pagination)
    """
    # Check if item exists
    item_exists = any(item.id == item_id for item in items_db)
    if not item_exists:
        raise HTTPException(status_code=404, detail="Item not found")

    # Filter images for the item
    images = [img for img in item_images_db if img.item_id == item_id]

    # Optional filter by primary flag
    if is_primary is not None:
        images = [img for img in images if img.is_primary == is_primary]

    # Apply pagination
    start = offset
    end = offset + limit
    return images[start:end]

# Get specific image
@app.get("/items/{item_id}/images/{image_id}", response_model=ItemImage, tags=["Item Images"])
async def get_item_image(item_id: int, image_id: int):
    """Get a specific image for an item"""
    for img in item_images_db:
        if img.id == image_id and img.item_id == item_id:
            return img
    raise HTTPException(status_code=404, detail="Image not found")

# Create new image for item
@app.post("/items/{item_id}/images", response_model=ItemImage, tags=["Item Images"])
async def create_item_image(item_id: int, image: ItemImageCreate):
    """Attach a new image to an item"""
    # Check if item exists
    item_exists = any(item.id == item_id for item in items_db)
    if not item_exists:
        raise HTTPException(status_code=404, detail="Item not found")
    
    global next_image_id
    now = datetime.now()
    new_image = ItemImage(
        id=next_image_id,
        item_id=item_id,
        image_url=image.image_url,
        alt_text=image.alt_text,
        is_primary=image.is_primary,
        created_at=now,
        updated_at=now
    )
    
    # If this is set as primary, unset other primary images for this item
    if image.is_primary:
        for img in item_images_db:
            if img.item_id == item_id:
                img.is_primary = False
    
    item_images_db.append(new_image)
    next_image_id += 1
    return new_image

# Update image
@app.put("/items/{item_id}/images/{image_id}", response_model=ItemImage, tags=["Item Images"])
async def update_item_image(item_id: int, image_id: int, image_update: ItemImageUpdate):
    """Update an item image"""
    for i, existing_image in enumerate(item_images_db):
        if existing_image.id == image_id and existing_image.item_id == item_id:
            # Update only provided fields
            update_data = image_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing_image, field, value)
            
            # If setting as primary, unset other primary images for this item
            if image_update.is_primary:
                for img in item_images_db:
                    if img.item_id == item_id and img.id != image_id:
                        img.is_primary = False
            
            existing_image.updated_at = datetime.now()
            return existing_image
    raise HTTPException(status_code=404, detail="Image not found")

# Delete image
@app.delete("/items/{item_id}/images/{image_id}", tags=["Item Images"])
async def delete_item_image(item_id: int, image_id: int):
    """Delete an item image"""
    for i, img in enumerate(item_images_db):
        if img.id == image_id and img.item_id == item_id:
            deleted_image = item_images_db.pop(i)
            return {"message": f"Image deleted successfully"}
    raise HTTPException(status_code=404, detail="Image not found")

if __name__ == "__main__":
    import os
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))