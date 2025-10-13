from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class ItemImageBase(BaseModel):
    item_id: int
    image_url: HttpUrl
    alt_text: Optional[str] = None
    is_primary: bool = False


class ItemImageCreate(BaseModel):
    image_url: HttpUrl
    alt_text: Optional[str] = None
    is_primary: bool = False


class ItemImageUpdate(BaseModel):
    image_url: Optional[HttpUrl] = None
    alt_text: Optional[str] = None
    is_primary: Optional[bool] = None


class ItemImage(ItemImageBase):
    id: int
    created_at: datetime
    updated_at: datetime
