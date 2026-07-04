from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.sale import Transaction, SaleItem
from app.models.product import Product
from app.schemas.transaction import TransactionCreate, TransactionOut, SaleItemOut

router = APIRouter(prefix="/transactions", tags=["transactions"])


def build_transaction_out(transaction: Transaction) -> TransactionOut:
    items = [
        SaleItemOut(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal,
            created_at=transaction.created_at,
        )
        for item in transaction.items
    ]
    return TransactionOut(
        id=transaction.id,
        total=transaction.total,
        created_at=transaction.created_at,
        items=items,
    )


@router.post("/", response_model=TransactionOut, status_code=201)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    sale_items = []
    total = 0

    for item_data in payload.items:
        product = db.get(Product, item_data.product_id)
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Product {item_data.product_id} not found"
            )

        subtotal = product.price * item_data.quantity
        total += subtotal

        sale_items.append(
            SaleItem(
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=product.price,
                subtotal=subtotal,
            )
        )

    transaction = Transaction(total=total, items=sale_items)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return build_transaction_out(transaction)


@router.get("/", response_model=List[TransactionOut])
def list_transactions(db: Session = Depends(get_db)):
    transactions = (
        db.query(Transaction).order_by(Transaction.created_at.desc()).all()
    )
    return [build_transaction_out(t) for t in transactions]


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return build_transaction_out(transaction)
