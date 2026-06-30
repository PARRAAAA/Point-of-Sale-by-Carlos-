from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import List


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int


class TransactionCreate(BaseModel):
    items: List[SaleItemCreate]


class SaleItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    created_at: datetime


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    total: Decimal
    created_at: datetime
    items: List[SaleItemOut]
