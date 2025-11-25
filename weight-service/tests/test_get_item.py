import pytest
from unittest.mock import patch

class TestGetItem:
    """Essential GET /item/<id> tests"""

    def test_get_item_registered_container(self, client, mock_get_db, mock_db, mock_datetime_item):
        """Container exists → return tara + sessions"""
        mock_conn, mock_cursor = mock_db

        # 1st fetchone: container lookup
        mock_cursor.fetchone.side_effect = [
            {"weight": 150}  # container tara
        ]

        # fetchall: sessions for this container
        mock_cursor.fetchall.return_value = [
            {"session_id": 1},
            {"session_id": 2},
            {"session_id": 5}
        ]

        response = client.get('/item/C1')
        data = response.get_json()

        assert response.status_code == 200
        assert data["id"] == "C1"
        assert data["tara"] == 150
        assert data["sessions"] == ["1", "2", "5"]

    def test_get_item_truck(self, client, mock_get_db, mock_db, mock_datetime_item):
        """Truck exists → return truck tara + sessions"""
        mock_conn, mock_cursor = mock_db

        # First fetchone: container lookup → None
        # Second fetchone: truck lookup → truckTara found
        mock_cursor.fetchone.side_effect = [
            None,                  # not a container
            {"truckTara": 2000}    # truck found
        ]

        mock_cursor.fetchall.return_value = [
            {"session_id": 10},
            {"session_id": 11}
        ]

        response = client.get('/item/123-45-678')
        data = response.get_json()

        assert response.status_code == 200
        assert data["id"] == "123-45-678"
        assert data["tara"] == 2000
        assert data["sessions"] == ["10", "11"]

    def test_get_item_not_found(self, client, mock_get_db, mock_db, mock_datetime_item):
        """Neither container nor truck exists → 404"""
        mock_conn, mock_cursor = mock_db

        # container lookup → None
        # truck lookup → None
        mock_cursor.fetchone.side_effect = [None, None]

        response = client.get('/item/NONEXISTENT')
        data = response.get_json()

        assert response.status_code == 404
        assert "Item not found" in data["error"]
