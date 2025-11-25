import pytest
from unittest.mock import patch

class TestGetSession:
    """Essential GET /session/<id> tests"""

    def test_get_session_out_direction(self, client, mock_get_db, mock_db):
        """OUT session must return full details (bruto, truckTara, neto)"""
        mock_conn, mock_cursor = mock_db

        mock_cursor.fetchone.return_value = {
            "id": 101,
            "direction": "out",
            "truck": "123-45-678",
            "bruto": 4800,
            "truckTara": 2000,
            "neto": 2550
        }

        response = client.get('/session/101')
        data = response.get_json()

        assert response.status_code == 200
        assert data["id"] == "101"
        assert data["truck"] == "123-45-678"
        assert data["bruto"] == 4800
        assert data["truckTara"] == 2000
        assert data["neto"] == 2550

    def test_get_session_not_found(self, client, mock_get_db, mock_db):
        """Missing session ID → 404"""
        mock_conn, mock_cursor = mock_db

        mock_cursor.fetchone.return_value = None

        response = client.get('/session/99999')
        data = response.get_json()

        assert response.status_code == 404
        assert "Session not found" in data["error"]
