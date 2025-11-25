import pytest
from unittest.mock import patch

class TestBatchWeight:
    """Tests for POST /batch-weight: filename-based ingestion"""

    @patch("os.path.isfile", return_value=True)
    @patch("Routes.post_batch_weight.process_csv", return_value=(3, []))
    def test_batch_weight_csv_success(self, mock_csv, mock_isfile, client):
        """CSV filename provided -> processed successfully"""
        response = client.post(
            "/batch-weight",
            json={"file": "containers.csv"}
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data["file"] == "containers.csv"
        assert data["processed"] == 3
        assert data["errors"] == []

    @patch("os.path.isfile", return_value=True)
    @patch("Routes.post_batch_weight.process_json", return_value=(2, []))
    def test_batch_weight_json_success(self, mock_json, mock_isfile, client):
        """JSON filename provided -> processed successfully"""
        response = client.post(
            "/batch-weight",
            json={"file": "containers.json"}
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data["file"] == "containers.json"
        assert data["processed"] == 2
        assert data["errors"] == []

    def test_batch_weight_missing_file_field(self, client):
        """Missing 'file' field -> 400"""
        response = client.post("/batch-weight", json={})
        assert response.status_code == 400
        assert "file" in response.get_json()["error"]

    def test_batch_weight_unsupported_format(self, client):
        """Unsupported extension -> 400"""
        response = client.post(
            "/batch-weight",
            json={"file": "data.exe"}
        )
        assert response.status_code == 400
        assert "Unsupported file format" in response.get_json()["error"]

    @patch("os.path.isfile", return_value=False)
    def test_batch_weight_file_not_found(self, mock_isfile, client):
        """Valid filename but file does not exist -> 404"""
        response = client.post(
            "/batch-weight",
            json={"file": "missing.csv"}
        )
        assert response.status_code == 404
        assert "not found" in response.get_json()["error"]

    @patch("os.path.isfile", return_value=True)
    @patch("Routes.post_batch_weight.process_csv", side_effect=Exception("boom"))
    def test_batch_weight_processing_error(self, mock_csv, mock_isfile, client):
        """process_csv raises error -> 500"""
        response = client.post(
            "/batch-weight",
            json={"file": "containers.csv"}
        )
        assert response.status_code == 500
        assert "Internal error" in response.get_json()["error"]
