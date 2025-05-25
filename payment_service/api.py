from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from domain.entities import Payment
from domain.repositories import PaymentRepository
import requests

ORDER_SERVICE_URL = "http://localhost:8000/orders/"

app = FastAPI(title="Payment Service", description="CRUD API для оплат", version="1.0")
repo = PaymentRepository()

class PaymentCreate(BaseModel):
    payment_id: int
    order_id: int
    amount: float

class PaymentUpdate(BaseModel):
    amount: float = None
    status: str = None

@app.post("/payments/", response_model=dict, summary="Створити оплату")
def create_payment(payment: PaymentCreate):
    # Перевірка існування замовлення через Order Service
    try:
        resp = requests.get(f"{ORDER_SERVICE_URL}{payment.order_id}")
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Order does not exist")
    except Exception:
        raise HTTPException(status_code=400, detail="Order Service unavailable")
    if repo.get(payment.payment_id):
        raise HTTPException(status_code=400, detail="Payment already exists")
    new_payment = Payment(payment.payment_id, payment.order_id, payment.amount, "NEW")
    repo.add(new_payment)
    return {"payment_id": new_payment.payment_id, "order_id": new_payment.order_id, "amount": new_payment.amount, "status": new_payment.status}

@app.get("/payments/{payment_id}", response_model=dict, summary="Отримати оплату")
def get_payment(payment_id: int):
    payment = repo.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"payment_id": payment.payment_id, "order_id": payment.order_id, "amount": payment.amount, "status": payment.status}

@app.get("/payments/", response_model=list, summary="Список оплат")
def list_payments():
    return [{"payment_id": p.payment_id, "order_id": p.order_id, "amount": p.amount, "status": p.status} for p in repo.list()]

@app.put("/payments/{payment_id}", response_model=dict, summary="Оновити оплату")
def update_payment(payment_id: int, payment: PaymentUpdate):
    updated = repo.update(payment_id, amount=payment.amount, status=payment.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"payment_id": updated.payment_id, "order_id": updated.order_id, "amount": updated.amount, "status": updated.status}

@app.delete("/payments/{payment_id}", response_model=dict, summary="Видалити оплату")
def delete_payment(payment_id: int):
    deleted = repo.delete(payment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment deleted"} 