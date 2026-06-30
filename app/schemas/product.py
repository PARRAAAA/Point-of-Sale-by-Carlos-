from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProductCreate(BaseModel):
    name: str
    price: float
    category: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    category: Optional[str] = None
