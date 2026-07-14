import enum
from sqlalchemy import (
    String,
    Column,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PaymentMethod(enum.Enum):
    cash = "cash"
    card = "card"


class TransactionStatus(enum.Enum):
    active = "active"
    refunded = "refunded"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    total = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    status = Column(SAEnum(TransactionStatus), nullable=False, server_default="active")

    items = relationship("SaleItem", back_populates="transaction")
    payment = relationship("Payment", back_populates="transaction", uselist=False)
    refund = relationship("Refund", back_populates="transaction", uselist=False)


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(
        Integer, ForeignKey("transactions.id"), nullable=False, unique=True
    )
    method = Column(SAEnum(PaymentMethod), nullable=False)
    amount_tendered = Column(Numeric(10, 2), nullable=False)
    change_given = Column(Numeric(10, 2), nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())

    transaction = relationship("Transaction", back_populates="payment")


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(
        Integer, ForeignKey("transactions.id"), nullable=False, unique=True
    )
    reason = Column(String, nullable=True)
    refunded_at = Column(DateTime, server_default=func.now())

    transaction = relationship("Transaction", back_populates="refund")
