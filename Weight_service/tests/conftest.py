import pytest
import sys
import os
from unittest.mock import MagicMock

# 1. Add the project root (Weight_service) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app import app as flask_app
import db  

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
    })
    # Disable key sorting so assertions on JSON order pass
    flask_app.json.sort_keys = False 
    # Disable key sorting so assertions on JSON order pass
    flask_app.json.sort_keys = False 
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_db(monkeypatch):
    """
    Fixture to mock the database connection globally.
    Patches db.pymysql.connect so ALL routes receive the mock.
    """
    """
    Fixture to mock the database connection globally.
    Patches db.pymysql.connect so ALL routes receive the mock.
    """
    def _patch_db(rows=None, side_effect=None):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Setup the context manager: with conn.cursor() as cur:
        # Setup the context manager: with conn.cursor() as cur:
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        if side_effect:
            # Simulate an error (like connection down or query failed)
            # We apply it to cursor creation and execution to catch multiple failure points
            # Simulate an error (like connection down or query failed)
            # We apply it to cursor creation and execution to catch multiple failure points
            mock_conn.cursor.side_effect = side_effect
            mock_cursor.execute.side_effect = side_effect
            mock_cursor.execute.side_effect = side_effect
        else:
            # Simulate successful data return
            # Simulate successful data return
            mock_cursor.fetchone.return_value = rows[0] if rows else None
            mock_cursor.fetchall.return_value = rows or []

        # Patch the 'connect' function inside the 'db' module's pymysql import.
        # This works for get_weight, get_health, post_weight, etc.
        monkeypatch.setattr(db.pymysql, "connect", lambda **kwargs: mock_conn)
        # Patch the 'connect' function inside the 'db' module's pymysql import.
        # This works for get_weight, get_health, post_weight, etc.
        monkeypatch.setattr(db.pymysql, "connect", lambda **kwargs: mock_conn)

        return mock_cursor

    return _patch_db