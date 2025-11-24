def test_get_session_in_direction(client, mock_db):
    """
    For direction='in':
    - truckTara and neto should NOT appear in response
    """
    mock_db(rows=[{
        "id": 1,
        "direction": "in",
        "truck": "TR123",
        "bruto": 3500,
        "truckTara": 2000,   # Should not appear
        "neto": 1500         # Should not appear
    }])

    rv = client.get("/session/1")
    assert rv.status_code == 200

    data = rv.get_json()
    assert data == {
        "id": "1",
        "truck": "TR123",
        "bruto": 3500
    }


def test_get_session_out_direction(client, mock_db):
    """
    For direction='out':
    - truckTara must appear
    - neto appears as int or "na"
    """
    mock_db(rows=[{
        "id": 2,
        "direction": "out",
        "truck": "TR987",
        "bruto": 8000,
        "truckTara": 3000,
        "neto": 5000
    }])

    rv = client.get("/session/2")
    assert rv.status_code == 200

    data = rv.get_json()
    assert data == {
        "id": "2",
        "truck": "TR987",
        "bruto": 8000,
        "truckTara": 3000,
        "neto": 5000
    }


def test_get_session_out_direction_neto_na(client, mock_db):
    """
    neto = None -> return "na"
    """
    mock_db(rows=[{
        "id": 3,
        "direction": "out",
        "truck": "TR555",
        "bruto": 7000,
        "truckTara": 2500,
        "neto": None
    }])

    rv = client.get("/session/3")
    assert rv.status_code == 200

    data = rv.get_json()
    assert data == {
        "id": "3",
        "truck": "TR555",
        "bruto": 7000,
        "truckTara": 2500,
        "neto": "na"
    }


def test_get_session_not_found(client, mock_db):
    """
    No session found => 404
    """
    mock_db(rows=[])  # fetchone returns None

    rv = client.get("/session/999")
    assert rv.status_code == 404

    data = rv.get_json()
    assert data == {"error": "Session not found"}


def test_get_session_db_failure(client, mock_db):
    """
    DB raises exception => 500
    """
    mock_db(side_effect=Exception("DB failed"))

    rv = client.get("/session/10")
    assert rv.status_code == 500

    data = rv.get_json()
    assert data == {"error": "Internal Server Error"}
