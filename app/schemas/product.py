from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal


class ProductCreate(BaseModel):
    name: str
    price: Decimal
    category: Optional[str] = None
    stock: int = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    stock: Optional[int] = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal
    category: Optional[str] = None
    stock: int
