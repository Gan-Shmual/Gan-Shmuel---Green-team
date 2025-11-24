import requests
import time
import pytest

def test_billing_health():
    response = requests.get("http://billing:8000/health")
    assert response.status_code == 200
    assert response.json()["service"] == "billing"

def test_weight_health():
    response = requests.get("http://weight:8000/health")
    assert response.status_code == 200
    assert response.json()["service"] == "weight"

def test_billing_index():
    response = requests.get("http://billing:8000/")
    assert "billing service" in response.text.lower()

def test_weight_index():
    response = requests.get("http://weight:8000/")
    assert "weight service" in response.text.lower()