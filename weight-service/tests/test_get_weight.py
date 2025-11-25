import pytest
from unittest.mock import patch
from datetime import datetime

class TestGetWeight:
    """Critical GET /weight tests"""

    def test_get_weight_default_params(self, client, mock_get_db, mock_db, mock_datetime):
        """GET /weight with default params (today, all directions)"""
        mock_conn, mock_cursor = mock_db

        mock_cursor.fetchall.return_value = [
            {
                "id": 1,
                "direction": "in",
                "datetime": datetime(2024, 1, 15, 10, 0, 0),
                "bruto": 5000,
                "neto": None,
                "produce": "orange",
                "containers": "C1,C2",
                "session_id": 1,
                "truck": "123-45-678",
                "truckTara": None
            }
        ]

        response = client.get('/weight')
        data = response.get_json()

        assert response.status_code == 200
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["direction"] == "in"
        assert data[0]["containers"] == ["C1", "C2"]

    def test_get_weight_with_date_range(self, client, mock_get_db, mock_db):
        """GET /weight respects provided t1 and t2"""
        mock_conn, mock_cursor = mock_db

        mock_cursor.fetchall.return_value = []

        response = client.get('/weight?t1=20240101000000&t2=20240131235959')
        assert response.status_code == 200

        call_args = mock_cursor.execute.call_args
        params = call_args[0][1]

        assert params[0] == datetime(2024, 1, 1, 0, 0, 0)
        assert params[1] == datetime(2024, 1, 31, 23, 59, 59)

    def test_get_weight_filter_in_only(self, client, mock_get_db, mock_db):
        """GET /weight?filter=in returns only 'in' direction"""
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = []

        response = client.get('/weight?filter=in')
        assert response.status_code == 200

        call_args = mock_cursor.execute.call_args
        params = call_args[0][1]

        assert "in" in params
        assert "out" not in params
        assert "none" not in params

    def test_get_weight_response_structure(self, client, mock_get_db, mock_db):
        """Response contains expected fields"""
        mock_conn, mock_cursor = mock_db

        mock_cursor.fetchall.return_value = [
            {
                "id": 100,
                "direction": "out",
                "datetime": datetime(2024, 1, 15, 11, 0, 0),
                "bruto": 4800,
                "neto": 2550,
                "produce": "orange",
                "containers": "C1,C2",
                "session_id": 100,
                "truck": "123-45-678",
                "truckTara": 2000
            }
        ]

        response = client.get('/weight')
        assert response.status_code == 200

        result = response.get_json()[0]

        assert "id" in result
        assert "datetime" in result
        assert "direction" in result
        assert "truck" in result
        assert "containers" in result
        assert "bruto" in result
        assert "truckTara" in result
        assert "neto" in result
        assert "produce" in result
        assert "session_id" in result
