import enum
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import List


class PaymentMethod(str, enum.Enum):
    cash = "cash"
    card = "card"


class PaymentCreate(BaseModel):
    method: PaymentMethod
    amount_tendered: Decimal


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    method: PaymentMethod
    amount_tendered: Decimal
    change_given: Decimal


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int


class TransactionCreate(BaseModel):
    items: List[SaleItemCreate]
    payment: PaymentCreate


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
    payment: PaymentOut
