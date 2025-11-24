import time
import requests

BASE = "http://localhost:5000"

def test_session_1001_exists():
    # Retry until service up (simple wait loop)
    timeout = 30
    start = time.time()
    while True:
        try:
            r = requests.get(f"{BASE}/session/1", timeout=2)
            break
        except requests.exceptions.ConnectionError:
            if time.time() - start > timeout:
                raise
            time.sleep(0.5)

    assert r.status_code == 200
    j = r.json()
    assert j["id"] == "1"
    assert "bruto" in j
