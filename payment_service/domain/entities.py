class Payment:
    def __init__(self, payment_id: int, order_id: int, amount: float, status: str):
        self.payment_id = payment_id
        self.order_id = order_id
        self.amount = amount
        self.status = status 