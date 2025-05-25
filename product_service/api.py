from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from domain.entities import Product
from domain.repositories import ProductRepository
from db import SessionLocal, init_db

app = FastAPI(title="Product Service", description="CRUD API для продуктів", version="1.0")

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int

class ProductUpdate(BaseModel):
    name: str = None
    price: float = None
    quantity: int = None

@app.post("/products/", response_model=dict, summary="Створити продукт")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    prod = repo.add(product.name, product.price, product.quantity)
    return {"id": prod.id, "name": prod.name, "price": prod.price, "quantity": prod.quantity}

@app.get("/products/{product_id}", response_model=dict, summary="Отримати продукт")
def get_product(product_id: int, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    prod = repo.get(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"id": prod.id, "name": prod.name, "price": prod.price, "quantity": prod.quantity}

@app.get("/products/", response_model=list, summary="Список продуктів")
def list_products(db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    return [{"id": p.id, "name": p.name, "price": p.price, "quantity": p.quantity} for p in repo.list()]

@app.put("/products/{product_id}", response_model=dict, summary="Оновити продукт")
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    updated = repo.update(product_id, name=product.name, price=product.price, quantity=product.quantity)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"id": updated.id, "name": updated.name, "price": updated.price, "quantity": updated.quantity}

@app.delete("/products/{product_id}", response_model=dict, summary="Видалити продукт")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    deleted = repo.delete(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"} 