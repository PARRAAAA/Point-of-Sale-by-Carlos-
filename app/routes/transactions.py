from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.sale import (
    Transaction,
    SaleItem,
    Payment,
    Refund,
    TransactionStatus as ModelTransactionStatus,
)
from app.models.product import Product
from app.schemas.transaction import (
    TransactionCreate,
    TransactionOut,
    SaleItemOut,
    PaymentOut,
    RefundCreate,
    RefundOut,
)

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
        status=transaction.status,
        items=items,
        payment=PaymentOut.model_validate(transaction.payment),
        refund=(
            RefundOut.model_validate(transaction.refund) if transaction.refund else None
        ),
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
        if product.stock < item_data.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for '{product.name}' (available: {product.stock})",
            )

        subtotal = product.price * item_data.quantity
        total += subtotal
        product.stock -= item_data.quantity

        sale_items.append(
            SaleItem(
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=product.price,
                subtotal=subtotal,
            )
        )

    if payload.payment.amount_tendered < total:
        raise HTTPException(
            status_code=400,
            detail=f"Cantidad recibida ({payload.payment.amount_tendered}) es inferior a ({total})",
        )

    change_given = payload.payment.amount_tendered - total

    transaction = Transaction(total=total, items=sale_items)
    db.add(transaction)
    db.flush()  # get transaction.id before creating Payment

    payment = Payment(
        transaction_id=transaction.id,
        method=payload.payment.method,
        amount_tendered=payload.payment.amount_tendered,
        change_given=change_given,
    )
    db.add(payment)
    db.commit()
    db.refresh(transaction)

    return build_transaction_out(transaction)


@router.get("/", response_model=List[TransactionOut])
def list_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).order_by(Transaction.created_at.desc()).all()
    return [build_transaction_out(t) for t in transactions]


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction no encontrada")
    return build_transaction_out(transaction)


@router.post("/{transaction_id}/refund", response_model=TransactionOut)
def refund_transaction(
    transaction_id: int,
    payload: RefundCreate,
    db: Session = Depends(get_db),
):
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction no encontrada")
    if transaction.status == ModelTransactionStatus.refunded:
        raise HTTPException(status_code=400, detail="Transaction already refunded")

    for item in transaction.items:
        product = db.get(Product, item.product_id)
        if product:
            product.stock += item.quantity

    refund = Refund(transaction_id=transaction.id, reason=payload.reason)
    transaction.status = ModelTransactionStatus.refunded
    db.add(refund)
    db.commit()
    db.refresh(transaction)

    return build_transaction_out(transaction)


@router.get("/{transaction_id}/refund", response_model=RefundOut)
def get_refund(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction no encontrada")
    if not transaction.refund:
        raise HTTPException(status_code=404, detail="Rembolso no encontrado")
    return transaction.refund
