import pytest

def test_get_unknown_success(client, mock_db):
    # 1. Setup Mock Data
    # The route expects rows with container_id, weight, and unit
    # Logic: WHERE weight IS NULL
    mock_rows = [
        {"container_id": "C-NULL-1", "weight": None, "unit": "kg"},
        {"container_id": "C-NULL-2", "weight": None, "unit": "lbs"}
    ]
    
    # Configure mock to return these rows
    mock_db(rows=mock_rows)

    # 2. Execute
    rv = client.get("/unknown")

    # 3. Assert
    assert rv.status_code == 200
    data = rv.get_json()
    
    # Verify we got a list with the correct data
    assert len(data) == 2
    assert data[0]["container_id"] == "C-NULL-1"
    assert data[0]["weight"] is None

def test_get_unknown_empty(client, mock_db):
    # 1. Setup Mock Data (Empty list)
    mock_db(rows=[])

    # 2. Execute
    rv = client.get("/unknown")

    # 3. Assert
    assert rv.status_code == 200
    assert rv.get_json() == []

def test_get_unknown_db_error(client, mock_db):
    # 1. Setup Mock to fail
    mock_db(side_effect=Exception("DB Down"))

    # 2. Execute
    rv = client.get("/unknown")

    # 3. Assert
    assert rv.status_code == 500
    assert "Database query failed" in rv.get_data(as_text=True)