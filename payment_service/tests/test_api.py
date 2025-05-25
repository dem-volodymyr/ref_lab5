import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests
import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)
# ...далі ваші тести...

client = TestClient(app)
# ...далі ваші тести...

client = TestClient(app)

ORDER_SERVICE_URL = "http://localhost:8000/orders/"

# Для інтеграційних тестів потрібен запущений Order Service!

class MockResp:
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}
    def json(self):
        return self._json

def test_create_payment(monkeypatch):
    def mock_get(url):
        return MockResp(200, {"id": 1, "total_amount": 40.0, "status": "NEW"})
    def mock_put(url, json):
        return MockResp(200)
    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(requests, "put", mock_put)
    resp = client.post("/payments/", json={"payment_id": 1, "order_id": 1, "amount": 40.0})
    assert resp.status_code == 200
    data = resp.json()
    assert data["order_id"] == 1
    assert data["amount"] == 40.0
    assert data["status"] == "NEW"

def test_create_payment_for_nonexistent_order(monkeypatch):
    def mock_get(url):
        return MockResp(404)
    monkeypatch.setattr(requests, "get", mock_get)
    resp = client.post("/payments/", json={"payment_id": 2, "order_id": 999, "amount": 10.0})
    assert resp.status_code == 400

def test_create_duplicate_payment(monkeypatch):
    def mock_get(url):
        class MockResp:
            status_code = 200
        return MockResp()
    monkeypatch.setattr(requests, "get", mock_get)
    # Створюємо перший платіж
    client.post("/payments/", json={"payment_id": 3, "order_id": 1, "amount": 10.0})
    # Дубльований платіж
    resp = client.post("/payments/", json={"payment_id": 3, "order_id": 1, "amount": 10.0})
    assert resp.status_code == 400

def test_get_payment():
    resp = client.get("/payments/1")
    assert resp.status_code in (200, 404)  # Може бути 404, якщо не створено

def test_list_payments():
    resp = client.get("/payments/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_update_payment(monkeypatch):
    def mock_get(url):
        class MockResp:
            status_code = 200
        return MockResp()
    monkeypatch.setattr(requests, "get", mock_get)
    client.post("/payments/", json={"payment_id": 4, "order_id": 1, "amount": 10.0})
    resp = client.put("/payments/4", json={"amount": 20.0, "status": "PAID"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["amount"] == 20.0
    assert data["status"] == "PAID"

def test_update_nonexistent_payment():
    resp = client.put("/payments/999", json={"amount": 10.0})
    assert resp.status_code == 404

def test_delete_payment():
    resp = client.delete("/payments/1")
    assert resp.status_code in (200, 404)

def test_delete_nonexistent_payment():
    resp = client.delete("/payments/999")
    assert resp.status_code == 404 