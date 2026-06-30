from fastapi import FastAPI
from app.database import engine, Base
from app.routes import products, transactions

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tienda Mamá")

app.include_router(products.router)
app.include_router(transactions.router)
