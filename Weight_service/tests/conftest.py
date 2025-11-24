import pytest
from unittest.mock import MagicMock
import importlib
import os

# Make sure we can import your app
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
import sys
sys.path.insert(0, PROJECT_ROOT)

@pytest.fixture
def app():
    # Import the Flask app from your package
    # Adjust import path to match your project: Weight_service.app
    from app import app as flask_app
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def fake_db_cursor():
    """A small factory for fake cursors"""
    class Cursor:
        def __init__(self, rows=None):
            self._rows = rows or []
            self._idx = 0
        def execute(self, *_args, **_kwargs):
            pass
        def fetchone(self):
            if not self._rows:
                return None
            return self._rows[0]
        def fetchall(self):
            return self._rows
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            pass

    return Cursor

@pytest.fixture
def fake_db_connection(monkeypatch, fake_db_cursor):
    """Monkeypatch db.get_db to return a connection whose cursor() yields our fake cursor."""
    import db as db_module

    class FakeConn:
        def __init__(self, rows=None):
            self._rows = rows
        def cursor(self):
            return fake_db_cursor(self._rows)
        def close(self):
            pass

    def _patch(rows=None):
        def _get_db():
            return FakeConn(rows)
        monkeypatch.setattr(db_module, "get_db", _get_db)
        return _get_db

    return _patch
