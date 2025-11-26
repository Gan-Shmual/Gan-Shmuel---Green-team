import pytest

class TestGetUnknown:
    """Essential tests for GET /unknown"""

    def test_get_unknown_containers_success(self, client, mock_get_db, mock_db):
        """Should return list of containers with unknown weight"""
        mock_conn, mock_cursor = mock_db

        mock_cursor.fetchall.return_value = [
            {"container_id": "C1", "weight": None, "unit": None},
            {"container_id": "C2", "weight": None, "unit": None}
        ]

        response = client.get('/unknown')
        data = response.get_json()

        assert response.status_code == 200
        assert len(data) == 2
        assert data[0]["container_id"] == "C1"
        assert data[1]["container_id"] == "C2"

        # SQL executed correctly
        sql_call = str(mock_cursor.execute.call_args)
        assert "containers_registered" in sql_call
        assert "weight IS NULL" in sql_call

    def test_get_unknown_database_error(self, client, mock_get_db, mock_db):
        """Database error → 500"""
        mock_conn, mock_cursor = mock_db

        mock_cursor.execute.side_effect = Exception("Database failed")

        response = client.get('/unknown')
        body = response.get_data(as_text=True)

        assert response.status_code == 500
        assert "Database query failed" in body
