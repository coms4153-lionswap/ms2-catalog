from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class ItemStatus(str, Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    status: ItemStatus = ItemStatus.AVAILABLE


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    status: Optional[ItemStatus] = None


class Item(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
