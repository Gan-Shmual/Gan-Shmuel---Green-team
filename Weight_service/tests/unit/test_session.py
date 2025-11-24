import pytest

def test_get_session_found_out(client, mock_db):
    # latest transaction is OUT
    row = {
        "id": 1001,
        "direction": "out",
        "truck": "77-123-45",
        "bruto": 5000,
        "truckTara": 5000,
        "neto": 0
    }
    mock_db(rows=[row])
    
    rv = client.get("/session/1001")
    assert rv.status_code == 200
    j = rv.get_json()
    
    # FIX: Compare with a string "1001", not integer 1001
    assert j["id"] == "1001" 
    assert j["truck"] == "77-123-45"
    assert j["bruto"] == 5000
    assert j["truckTara"] == 5000
    assert j["neto"] == 0

def test_get_session_in_only(client, mock_db):
    row = {
        "id": 1002,
        "direction": "in",
        "truck": "88-999-00",
        "bruto": 30000,
        "truckTara": None,
        "neto": None
    }
    mock_db(rows=[row])
    
    rv = client.get("/session/1002")
    assert rv.status_code == 200
    j = rv.get_json()
    assert "truckTara" not in j or j["truckTara"] is None
    assert "neto" not in j or j["neto"] is None

def test_get_session_not_found(client, mock_db):
    mock_db(rows=[])
    rv = client.get("/session/9999")
    assert rv.status_code == 404