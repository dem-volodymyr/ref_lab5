from .entities import Payment

class PaymentRepository:
    def __init__(self):
        self.payments = {}

    def add(self, payment: Payment):
        self.payments[payment.payment_id] = payment

    def get(self, payment_id: int):
        return self.payments.get(payment_id)

    def list(self):
        return list(self.payments.values())

    def update(self, payment_id: int, amount: float = None, status: str = None):
        payment = self.payments.get(payment_id)
        if payment:
            if amount is not None:
                payment.amount = amount
            if status is not None:
                payment.status = status
            return payment
        return None

    def delete(self, payment_id: int):
        return self.payments.pop(payment_id, None) 