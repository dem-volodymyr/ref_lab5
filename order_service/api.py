from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from domain.repositories import OrderRepository
from db import SessionLocal, init_db
import requests

PRODUCT_SERVICE_URL = "http://localhost:8002/products/"

app = FastAPI(title="Order Service", description="CRUD API для замовлень", version="2.0")

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class OrderItemIn(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: list[OrderItemIn]

class OrderStatusUpdate(BaseModel):
    status: str

@app.post("/orders/", response_model=dict, summary="Створити замовлення")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Перевірка наявності продуктів і підрахунок total_amount
    items_data = []
    total_amount = 0.0
    for item in order.items:
        resp = requests.get(f"{PRODUCT_SERVICE_URL}{item.product_id}")
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
        prod = resp.json()
        if prod["quantity"] < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough quantity for product {item.product_id}")
        # Зменшуємо залишок у Product Service
        patch_resp = requests.put(f"{PRODUCT_SERVICE_URL}{item.product_id}", json={"quantity": prod["quantity"] - item.quantity})
        if patch_resp.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Failed to update product {item.product_id}")
        items_data.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price_at_order": prod["price"]
        })
        total_amount += prod["price"] * item.quantity
    repo = OrderRepository(db)
    new_order = repo.add(items=items_data, total_amount=total_amount)
    return {
        "id": new_order.id,
        "items": [{"product_id": i.product_id, "quantity": i.quantity, "price_at_order": i.price_at_order} for i in new_order.items],
        "total_amount": new_order.total_amount,
        "status": new_order.status
    }

@app.get("/orders/{order_id}", response_model=dict, summary="Отримати замовлення")
def get_order(order_id: int, db: Session = Depends(get_db)):
    repo = OrderRepository(db)
    order = repo.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "id": order.id,
        "items": [{"product_id": i.product_id, "quantity": i.quantity, "price_at_order": i.price_at_order} for i in order.items],
        "total_amount": order.total_amount,
        "status": order.status
    }

@app.get("/orders/", response_model=list, summary="Список замовлень")
def list_orders(db: Session = Depends(get_db)):
    repo = OrderRepository(db)
    return [{
        "id": o.id,
        "items": [{"product_id": i.product_id, "quantity": i.quantity, "price_at_order": i.price_at_order} for i in o.items],
        "total_amount": o.total_amount,
        "status": o.status
    } for o in repo.list()]

@app.put("/orders/{order_id}/status", response_model=dict, summary="Оновити статус замовлення")
def update_order_status(order_id: int, update: OrderStatusUpdate, db: Session = Depends(get_db)):
    repo = OrderRepository(db)
    updated = repo.update_status(order_id, update.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "id": updated.id,
        "status": updated.status
    }

@app.delete("/orders/{order_id}", response_model=dict, summary="Видалити замовлення")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    repo = OrderRepository(db)
    deleted = repo.delete(order_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted"} 