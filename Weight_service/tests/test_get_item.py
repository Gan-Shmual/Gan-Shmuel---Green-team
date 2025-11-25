import pytest
from unittest.mock import MagicMock

def test_get_item_container_found(client, mock_db):
    """Test finding a registered container."""
    # 1. Setup Mock Data
    # Query 1 (fetchone): Check Container -> Returns result
    # Query 2 (fetchall): Get Sessions -> Returns list of sessions
    
    # We use .side_effect for fetchone to simulate the sequence of calls
    container_data = {"weight": 500}
    session_data = [{"session_id": 1001}, {"session_id": 1002}]

    # Initialize mock (we handle specific returns manually below)
    mock_cursor = mock_db() 
    
    # Configure the sequence of returns
    mock_cursor.fetchone.side_effect = [container_data] 
    mock_cursor.fetchall.return_value = session_data

    # 2. Execute
    rv = client.get("/item/C-100")

    # 3. Assert
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["id"] == "C-100"
    assert data["tara"] == 500
    assert data["sessions"] == ["1001", "1002"]

def test_get_item_truck_found(client, mock_db):
    """Test finding a truck (container check fails, truck check succeeds)."""
    # 1. Setup Mock Data
    # Query 1 (fetchone): Check Container -> Returns None (Not found)
    # Query 2 (fetchone): Check Truck -> Returns result
    # Query 3 (fetchall): Get Sessions -> Returns list
    
    truck_data = {"truckTara": 2000}
    session_data = [{"session_id": 500}]

    mock_cursor = mock_db()
    
    # Sequence: None (Container), Truck Data (Truck)
    mock_cursor.fetchone.side_effect = [None, truck_data]
    mock_cursor.fetchall.return_value = session_data

    # 2. Execute
    rv = client.get("/item/T-123")

    # 3. Assert
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["id"] == "T-123"
    assert data["tara"] == 2000
    assert data["sessions"] == ["500"]

def test_get_item_not_found(client, mock_db):
    """Test when neither container nor truck is found."""
    # Both queries return None
    mock_cursor = mock_db()
    mock_cursor.fetchone.side_effect = [None, None]

    rv = client.get("/item/UNKNOWN_ID")

    assert rv.status_code == 404
    assert "Item not found" in rv.get_data(as_text=True)