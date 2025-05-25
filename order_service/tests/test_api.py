import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from api import app
import requests

client = TestClient(app)

class MockResp:
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}
    def json(self):
        return self._json

def test_create_order(monkeypatch):
    def mock_get(url):
        return MockResp(200, {"id": 1, "name": "Apple", "price": 10.0, "quantity": 100})
    def mock_put(url, json):
        return MockResp(200)
    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(requests, "put", mock_put)
    resp = client.post("/orders/", json={"items": [{"product_id": 1, "quantity": 2}]})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_amount"] == 20.0
    assert data["status"] == "NEW"

def test_create_order_not_enough_quantity(monkeypatch):
    def mock_get(url):
        return MockResp(200, {"id": 1, "name": "Apple", "price": 10.0, "quantity": 1})
    def mock_put(url, json):
        return MockResp(200)
    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(requests, "put", mock_put)
    resp = client.post("/orders/", json={"items": [{"product_id": 1, "quantity": 2}]})
    assert resp.status_code == 400
    assert "Not enough quantity" in resp.json()["detail"]

def test_create_order_product_not_found(monkeypatch):
    def mock_get(url):
        return MockResp(404)
    def mock_put(url, json):
        return MockResp(200)
    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(requests, "put", mock_put)
    resp = client.post("/orders/", json={"items": [{"product_id": 999, "quantity": 1}]})
    assert resp.status_code == 400
    assert "Product 999 not found" in resp.json()["detail"]

def test_get_order():
    resp = client.get("/orders/1")
    assert resp.status_code in (200, 404)

def test_list_orders():
    resp = client.get("/orders/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_delete_order(monkeypatch):
    # Створюємо замовлення для видалення
    def mock_get(url):
        return MockResp(200, {"id": 2, "name": "Banana", "price": 5.0, "quantity": 100})
    def mock_put(url, json):
        return MockResp(200)
    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(requests, "put", mock_put)
    resp = client.post("/orders/", json={"items": [{"product_id": 2, "quantity": 1}]})
    order_id = resp.json()["id"]
    resp = client.delete(f"/orders/{order_id}")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Order deleted"

def test_delete_nonexistent_order():
    resp = client.delete("/orders/999")
    assert resp.status_code == 404

def test_update_order_status(monkeypatch):
    # Створюємо замовлення для оновлення статусу
    def mock_get(url):
        return MockResp(200, {"id": 3, "name": "Milk", "price": 20.0, "quantity": 100})
    def mock_put(url, json):
        return MockResp(200)
    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(requests, "put", mock_put)
    resp = client.post("/orders/", json={"items": [{"product_id": 3, "quantity": 1}]})
    order_id = resp.json()["id"]
    resp = client.put(f"/orders/{order_id}/status", json={"status": "PAID"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "PAID" 