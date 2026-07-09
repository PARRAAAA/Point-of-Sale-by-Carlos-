from fastapi import FastAPI
from app.routes import products, transactions

app = FastAPI(title="Tienda Mamá")

app.include_router(products.router)
app.include_router(transactions.router)
