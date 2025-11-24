import requests
import time
import pytest


BASE = "http://weight-app:5000"
#helper func to wait for the service(db included)
def wait_for_service(timeout=30):
    start = time.time()
    while True:
        try:
            r = requests.get(f"{BASE}/health", timeout=2)
            if r.status_code == 200:
                return
        except requests.exceptions.RequestException:
            
            pass

        if time.time() - start > timeout:
            raise TimeoutError("weight service did not become healthy in time")

        time.sleep(1)

def test_weight_health():
    wait_for_service()
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200


