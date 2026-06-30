from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base 


class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
