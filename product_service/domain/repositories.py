from sqlalchemy.orm import Session
from .entities import Product

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, product_id: int):
        return self.db.query(Product).filter(Product.id == product_id).first()

    def list(self):
        return self.db.query(Product).all()

    def add(self, name: str, price: float, quantity: int):
        product = Product(name=name, price=price, quantity=quantity)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def update(self, product_id: int, name: str = None, price: float = None, quantity: int = None):
        product = self.get(product_id)
        if not product:
            return None
        if name is not None:
            product.name = name
        if price is not None:
            product.price = price
        if quantity is not None:
            product.quantity = quantity
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: int):
        product = self.get(product_id)
        if not product:
            return None
        self.db.delete(product)
        self.db.commit()
        return product 