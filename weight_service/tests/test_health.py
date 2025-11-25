import pytest

class TestHealthEndpoint:
    """Essential tests for GET /health"""

    def test_health_success(self, client, mock_get_db, mock_db):
        """Database is reachable → return 200 OK"""
        mock_conn, mock_cursor = mock_db

        mock_cursor.execute.return_value = None  # SELECT 1 passes

        response = client.get('/health')

        assert response.status_code == 200
        assert response.data == b'OK'
        mock_cursor.execute.assert_called_once_with("SELECT 1;")

    def test_health_database_failure(self, client, mock_get_db):
        """get_db itself fails → return 500"""
        mock_get_db.side_effect = Exception("Database connection failed")

        response = client.get('/health')

        assert response.status_code == 500
        assert response.data == b'Failure'

    def test_health_query_failure(self, client, mock_get_db, mock_db):
        """DB connection works but SELECT 1 fails → return 500"""
        mock_conn, mock_cursor = mock_db

        mock_cursor.execute.side_effect = Exception("Query failed")

        response = client.get('/health')

        assert response.status_code == 500
        assert response.data == b'Failure'
