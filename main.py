from fastapi import FastAPI, HTTPException, Query, Depends, UploadFile, File
from typing import List, Optional
from datetime import datetime
import uvicorn
import os
import shutil

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

from fastapi.responses import FileResponse

from models.item import Item, ItemCreate, ItemUpdate, ItemStatus
from models.item_image import ItemImage, ItemImageCreate, ItemImageUpdate

# Create FastAPI instance
app = FastAPI(
    title="Catalog Service API",
    description="Microservice for managing catalog items and item images",
    version="1.0.0",
)

# ==== DATABASE CONFIGURATION ====
# Use DATABASE_URL environment variable if provided (Cloud Run / production),
# otherwise fall back to a local SQLite file for local development.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./catalog.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Directory to store uploaded image files (for local and Cloud Run ephemeral storage)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== ORM MODELS ====
class ItemORM(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1024))
    price = Column(Float)
    category = Column(String(255))
    # store status as string; map to ItemStatus enum in Pydantic models
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    images = relationship(
        "ItemImageORM", back_populates="item", cascade="all, delete-orphan"
    )


class ItemImageORM(Base):
    __tablename__ = "item_images"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    image_url = Column(String(2048), nullable=False)
    alt_text = Column(String(255))
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    item = relationship("ItemORM", back_populates="images")


# Create tables if they do not exist (useful for local dev / SQLite)
Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    db: Session = Depends(get_db),
):
    """
    Get catalog items with optional filtering and pagination.
    """
    query = db.query(ItemORM)

    if category is not None:
        query = query.filter(ItemORM.category.ilike(category))

    if status is not None:
        # status is an ItemStatus enum; store its value as string in DB
        query = query.filter(ItemORM.status == status.value)

    if min_price is not None:
        query = query.filter(ItemORM.price >= min_price)

    if max_price is not None:
        query = query.filter(ItemORM.price <= max_price)

    items = query.offset(offset).limit(limit).all()

    return [
        Item(
            id=i.id,
            name=i.name,
            description=i.description,
            price=i.price,
            category=i.category,
            status=ItemStatus(i.status) if i.status is not None else None,
            created_at=i.created_at,
            updated_at=i.updated_at,
        )
        for i in items
    ]

# Get item by ID
@app.get("/items/{item_id}", response_model=Item, tags=["Items"])
async def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific item by ID"""
    db_item = db.query(ItemORM).filter(ItemORM.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return Item(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        category=db_item.category,
        status=ItemStatus(db_item.status) if db_item.status is not None else None,
        created_at=db_item.created_at,
        updated_at=db_item.updated_at,
    )

# Create new item
@app.post("/items", response_model=Item, tags=["Items"])
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new catalog item"""
    now = datetime.now()
    db_item = ItemORM(
        name=item.name,
        description=item.description,
        price=item.price,
        category=item.category,
        status=item.status.value if item.status is not None else None,
        created_at=now,
        updated_at=now,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return Item(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        category=db_item.category,
        status=ItemStatus(db_item.status) if db_item.status is not None else None,
        created_at=db_item.created_at,
        updated_at=db_item.updated_at,
    )

# Update item
@app.put("/items/{item_id}", response_model=Item, tags=["Items"])
async def update_item(item_id: int, item_update: ItemUpdate, db: Session = Depends(get_db)):
    """Update an existing item"""
    db_item = db.query(ItemORM).filter(ItemORM.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and value is not None:
            setattr(db_item, field, value.value)
        else:
            setattr(db_item, field, value)

    db_item.updated_at = datetime.now()
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return Item(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        category=db_item.category,
        status=ItemStatus(db_item.status) if db_item.status is not None else None,
        created_at=db_item.created_at,
        updated_at=db_item.updated_at,
    )

# Delete item
@app.delete("/items/{item_id}", tags=["Items"])
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item and all its associated images"""
    db_item = db.query(ItemORM).filter(ItemORM.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    name = db_item.name
    db.delete(db_item)
    db.commit()
    return {"message": f"Item '{name}' and its images deleted successfully"}

# Get items by category
@app.get("/items/category/{category}", response_model=List[Item], tags=["Items"])
async def get_items_by_category(category: str, db: Session = Depends(get_db)):
    """Get all items in a specific category"""
    items = (
        db.query(ItemORM)
        .filter(ItemORM.category.ilike(category))
        .all()
    )
    return [
        Item(
            id=i.id,
            name=i.name,
            description=i.description,
            price=i.price,
            category=i.category,
            status=ItemStatus(i.status) if i.status is not None else None,
            created_at=i.created_at,
            updated_at=i.updated_at,
        )
        for i in items
    ]

# Get items by status
@app.get("/items/status/{status}", response_model=List[Item], tags=["Items"])
async def get_items_by_status(status: ItemStatus, db: Session = Depends(get_db)):
    """Get all items with a specific status"""
    items = db.query(ItemORM).filter(ItemORM.status == status.value).all()
    return [
        Item(
            id=i.id,
            name=i.name,
            description=i.description,
            price=i.price,
            category=i.category,
            status=ItemStatus(i.status) if i.status is not None else None,
            created_at=i.created_at,
            updated_at=i.updated_at,
        )
        for i in items
    ]

# ===== ITEM IMAGES ENDPOINTS =====

# Get all images for an item with optional filtering and pagination
@app.get("/items/{item_id}/images", response_model=List[ItemImage], tags=["Item Images"])
async def get_item_images(
    item_id: int,
    is_primary: Optional[bool] = Query(None, description="Filter to only primary or non-primary images"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of images to return"),
    offset: int = Query(0, ge=0, description="Number of images to skip from the start"),
    db: Session = Depends(get_db),
):
    """
    Get images for a specific item with optional filtering and pagination.
    """
    # Check if item exists
    item_exists = db.query(ItemORM).filter(ItemORM.id == item_id).first()
    if item_exists is None:
        raise HTTPException(status_code=404, detail="Item not found")

    query = db.query(ItemImageORM).filter(ItemImageORM.item_id == item_id)

    if is_primary is not None:
        query = query.filter(ItemImageORM.is_primary == is_primary)

    images = query.offset(offset).limit(limit).all()

    return [
        ItemImage(
            id=img.id,
            item_id=img.item_id,
            image_url=img.image_url,
            alt_text=img.alt_text,
            is_primary=img.is_primary,
            created_at=img.created_at,
            updated_at=img.updated_at,
        )
        for img in images
    ]

# Get specific image
@app.get("/items/{item_id}/images/{image_id}", response_model=ItemImage, tags=["Item Images"])
async def get_item_image(item_id: int, image_id: int, db: Session = Depends(get_db)):
    """Get a specific image for an item"""
    img = (
        db.query(ItemImageORM)
        .filter(ItemImageORM.id == image_id, ItemImageORM.item_id == item_id)
        .first()
    )
    if img is None:
        raise HTTPException(status_code=404, detail="Image not found")

    return ItemImage(
        id=img.id,
        item_id=img.item_id,
        image_url=img.image_url,
        alt_text=img.alt_text,
        is_primary=img.is_primary,
        created_at=img.created_at,
        updated_at=img.updated_at,
    )

# Create new image for item
@app.post("/items/{item_id}/images", response_model=ItemImage, tags=["Item Images"])
async def create_item_image(item_id: int, image: ItemImageCreate, db: Session = Depends(get_db)):
    """Attach a new image to an item"""
    # Check if item exists
    item_exists = db.query(ItemORM).filter(ItemORM.id == item_id).first()
    if item_exists is None:
        raise HTTPException(status_code=404, detail="Item not found")

    now = datetime.now()

    # If this is set as primary, unset other primary images for this item
    if image.is_primary:
        db.query(ItemImageORM).filter(
            ItemImageORM.item_id == item_id,
            ItemImageORM.is_primary == True,  # noqa: E712
        ).update({"is_primary": False})

    db_image = ItemImageORM(
        item_id=item_id,
        image_url=image.image_url,
        alt_text=image.alt_text,
        is_primary=image.is_primary,
        created_at=now,
        updated_at=now,
    )

    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    return ItemImage(
        id=db_image.id,
        item_id=db_image.item_id,
        image_url=db_image.image_url,
        alt_text=db_image.alt_text,
        is_primary=db_image.is_primary,
        created_at=db_image.created_at,
        updated_at=db_image.updated_at,
    )

# Update image
@app.put("/items/{item_id}/images/{image_id}", response_model=ItemImage, tags=["Item Images"])
async def update_item_image(
    item_id: int,
    image_id: int,
    image_update: ItemImageUpdate,
    db: Session = Depends(get_db),
):
    """Update an item image"""
    db_image = (
        db.query(ItemImageORM)
        .filter(ItemImageORM.id == image_id, ItemImageORM.item_id == item_id)
        .first()
    )
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    update_data = image_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_image, field, value)

    # If setting as primary, unset other primary images for this item
    if image_update.is_primary:
        db.query(ItemImageORM).filter(
            ItemImageORM.item_id == item_id,
            ItemImageORM.id != image_id,
            ItemImageORM.is_primary == True,  # noqa: E712
        ).update({"is_primary": False})

    db_image.updated_at = datetime.now()
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    return ItemImage(
        id=db_image.id,
        item_id=db_image.item_id,
        image_url=db_image.image_url,
        alt_text=db_image.alt_text,
        is_primary=db_image.is_primary,
        created_at=db_image.created_at,
        updated_at=db_image.updated_at,
    )

# Delete image
@app.delete("/items/{item_id}/images/{image_id}", tags=["Item Images"])
async def delete_item_image(item_id: int, image_id: int, db: Session = Depends(get_db)):
    """Delete an item image"""
    db_image = (
        db.query(ItemImageORM)
        .filter(ItemImageORM.id == image_id, ItemImageORM.item_id == item_id)
        .first()
    )
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    db.delete(db_image)
    db.commit()
    return {"message": "Image deleted successfully"}


# ===== IMAGE UPLOAD / SERVE ENDPOINTS =====

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image file and return a URL that can be used to display it.

    This endpoint saves the file under the local `uploads` directory and
    returns a relative URL like `/images/{filename}`. The frontend can then
    render the image via an <img> tag using that URL.
    """
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded file to disk
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"image_url": f"/images/{file.filename}"}


@app.get("/images/{filename}")
async def get_uploaded_image(filename: str):
    """Serve an uploaded image file by filename."""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(file_path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))