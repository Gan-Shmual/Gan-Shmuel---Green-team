import requests
import time
import pytest


WEIGHT_BASE = "http://weight-service:5000"
#helper func to wait for the service(db included)
def wait_for_weight_service(timeout=30):
    start = time.time()
    while True:
        try:
            r = requests.get(f"{WEIGHT_BASE}/health", timeout=2)
            if r.status_code == 200:
                return
        except requests.exceptions.RequestException:
            
            pass

        if time.time() - start > timeout:
            raise TimeoutError("weight service did not become healthy in time")

        time.sleep(1)

def test_weight_health():
    wait_for_weight_service()
    r = requests.get(f"{WEIGHT_BASE}/health")
    assert r.status_code == 200

BILLING_BASE = "http://billing-service:5001"

def wait_for_billing_service(timeout=30):
    start = time.time()
    while True:
        try:
            r = requests.get(f"{BILLING_BASE}/health", timeout=2)
            if r.status_code == 200:
                return
        except requests.exceptions.RequestException:
            
            pass

        if time.time() - start > timeout:
            raise TimeoutError("Billing service did not become healthy in time")

        time.sleep(1)

def test_billing_health():
    wait_for_billing_service()
    r = requests.get(f"{BILLING_BASE}/health")
    assert r.status_code == 200




