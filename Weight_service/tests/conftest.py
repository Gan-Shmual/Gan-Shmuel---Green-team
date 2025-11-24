import pytest
import sys
import os
from unittest.mock import MagicMock

# 1. Add the parent directory (Weight_service) to sys.path
# This ensures we can import 'app' and 'db' correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_db(monkeypatch):
    import Routes.get_health as health_route  # <--- patch where it is used

    def _patch_db(rows=None, side_effect=None):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        if side_effect:
            mock_conn.cursor.side_effect = side_effect
        else:
            mock_cursor.fetchone.return_value = rows[0] if rows else None
            mock_cursor.fetchall.return_value = rows or []

        # Patch the function *inside the get_health module*
        monkeypatch.setattr(health_route, "get_db", lambda: mock_conn)

        return mock_cursor

    return _patch_db
