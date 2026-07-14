import enum
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from enum import StrEnum


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


class TransactionStatus(StrEnum):
    active = "active"
    refunded = "refunded"


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
    status: TransactionStatus
    created_at: datetime


class RefundCreate(BaseModel):
    reason: Optional[str] = None


class RefundOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reason: Optional[str] = None
    refunded_at: datetime


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    total: Decimal
    created_at: datetime
    status: TransactionStatus
    items: List[SaleItemOut]
    payment: PaymentOut
    refund: Optional[RefundOut] = None
