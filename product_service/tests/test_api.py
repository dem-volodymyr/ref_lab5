import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests
import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_create_product():
    resp = client.post("/products/", json={"name": "Test", "price": 99.9, "quantity": 10})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test"
    assert data["price"] == 99.9
    assert data["quantity"] == 10

def test_list_products():
    resp = client.get("/products/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_update_product():
    resp = client.post("/products/", json={"name": "ToUpdate", "price": 10, "quantity": 5})
    prod_id = resp.json()["id"]
    resp = client.put(f"/products/{prod_id}", json={"name": "Updated", "price": 20, "quantity": 3})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"

def test_delete_product():
    resp = client.post("/products/", json={"name": "ToDelete", "price": 1, "quantity": 1})
    prod_id = resp.json()["id"]
    resp = client.delete(f"/products/{prod_id}")
    assert resp.status_code == 200 