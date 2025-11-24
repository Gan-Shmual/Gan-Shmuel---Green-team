def test_get_session_found_out(client, fake_db_connection):
    # latest transaction is OUT
    row = {
        "direction": "out",
        "truck": "77-123-45",
        "bruto": 5000,
        "truckTara": 5000,
        "neto": 0
    }
    fake_db_connection(rows=[row])
    rv = client.get("/session/1001")
    assert rv.status_code == 200
    j = rv.get_json()
    assert j["id"] == "1001"
    assert j["truck"] == "77-123-45"
    assert j["bruto"] == 5000
    assert j["truckTara"] == 5000
    assert j["neto"] == 0

def test_get_session_in_only(client, fake_db_connection):
    row = {
        "direction": "in",
        "truck": "88-999-00",
        "bruto": 30000,
        "truckTara": None,
        "neto": None
    }
    fake_db_connection(rows=[row])
    rv = client.get("/session/1002")
    assert rv.status_code == 200
    j = rv.get_json()
    assert "truckTara" not in j
    assert "neto" not in j

def test_get_session_not_found(client, fake_db_connection):
    fake_db_connection(rows=[])
    rv = client.get("/session/9999")
    assert rv.status_code == 404
