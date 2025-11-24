from datetime import datetime

def test_get_weight_success(client, mock_db):
    # 1. Prepare Mock Data
    # The route expects a dictionary because of DictCursor, 
    # and 'datetime' must be a real datetime object for strftime() to work.
    mock_rows = [
        {
            "id": 1001,
            "datetime": datetime(2025, 11, 24, 10, 0, 0),
            "direction": "in",
            "truck": "T-123",
            "containers": "C-1,C-2",
            "bruto": 5000,
            "truckTara": 2000,
            "neto": 3000,
            "produce": "oranges",
            "session_id": 1001
        }
    ]
    
    # 2. Configure Mock
    mock_db(rows=mock_rows)
    
    # 3. Execute Request
    rv = client.get("/weight")
    
    # 4. Assertions
    assert rv.status_code == 200
    data = rv.get_json()
    
    assert len(data) == 1
    assert data[0]['id'] == 1001
    assert data[0]['direction'] == "in"
    # Verify container splitting logic works
    assert data[0]['containers'] == ["C-1", "C-2"]
    # Verify date formatting works
    assert data[0]['datetime'] == "2025-11-24 10:00:00"

def test_get_weight_with_filters(client, mock_db):
    """Test passing query parameters (t1, t2, filter)"""
    mock_rows = [] # Return empty for this test, mostly checking no crash
    mock_db(rows=mock_rows)

    # Pass valid YYYYMMDDHHMMSS dates
    t1 = "20250101000000"
    t2 = "20250102000000"
    rv = client.get(f"/weight?t1={t1}&t2={t2}&filter=out")
    
    assert rv.status_code == 200
    assert rv.get_json() == []

def test_get_weight_invalid_date(client, mock_db):
    """Test that bad date format returns 400"""
    # No DB mock needed as it fails before DB call
    
    rv = client.get("/weight?t1=INVALID_DATE")
    
    assert rv.status_code == 400
    assert "Invalid date format" in rv.get_data(as_text=True)

def test_get_weight_db_failure(client, mock_db):
    """Test handling of database exceptions"""
    # Simulate DB connection drop or query error
    mock_db(side_effect=Exception("DB Connection Timeout"))
    
    rv = client.get("/weight")
    
    assert rv.status_code == 500
    json_data = rv.get_json()
    assert json_data["error"] == "Database error"