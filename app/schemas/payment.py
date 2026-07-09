from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal


class ProductSale(BaseModel):
    name: str
    price: decimal
    category: Optional[str] = None
    stock: int = 0
