from sqlalchemy.orm import Session
from .entities import Order, OrderItem

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, order_id: int):
        return self.db.query(Order).filter(Order.id == order_id).first()

    def list(self):
        return self.db.query(Order).all()

    def add(self, items: list, total_amount: float):
        order = Order(total_amount=total_amount, status='NEW')
        self.db.add(order)
        self.db.flush()  # отримати order.id
        for item in items:
            order_item = OrderItem(order_id=order.id, product_id=item['product_id'], quantity=item['quantity'], price_at_order=item['price_at_order'])
            self.db.add(order_item)
        self.db.commit()
        self.db.refresh(order)
        return order

    def update_status(self, order_id: int, status: str):
        order = self.get(order_id)
        if not order:
            return None
        order.status = status
        self.db.commit()
        self.db.refresh(order)
        return order

    def update(self, order_id: int, amount: float = None, status: str = None):
        order = self.get(order_id)
        if order:
            if amount is not None:
                order.amount = amount
            if status is not None:
                order.status = status
            self.db.commit()
            self.db.refresh(order)
            return order
        return None

    def delete(self, order_id: int):
        order = self.get(order_id)
        if order:
            self.db.delete(order)
            self.db.commit()
            return order
        return None 