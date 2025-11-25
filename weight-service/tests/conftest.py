import pytest
import sys
import os
import builtins
from unittest.mock import MagicMock

# -------------------------------------------------------------
#  Ensure project root is importable
# -------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app import app as flask_app
import db

# Import all route modules that call get_db()
import Routes.post_weight as pw
import Routes.get_weight as gw
import Routes.get_session as gs
import Routes.get_item as gi
import Routes.get_unknown as gu
import Routes.get_health as gh
import Routes.post_batch_weight as pb


# -------------------------------------------------------------
#  APP + CLIENT FIXTURES
# -------------------------------------------------------------
@pytest.fixture
def app():
    flask_app.config.update({"TESTING": True})
    flask_app.json.sort_keys = False
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


# -------------------------------------------------------------
#  UTILITY FUNCTION — patches get_db in ALL modules
# -------------------------------------------------------------
def patch_all_get_db(monkeypatch, conn):
    """
    Ensures ALL modules use the SAME mock DB connection.
    """
    monkeypatch.setattr(db, "get_db", lambda: conn)
    monkeypatch.setattr(pw, "get_db", lambda: conn)
    monkeypatch.setattr(gw, "get_db", lambda: conn)
    monkeypatch.setattr(gs, "get_db", lambda: conn)
    monkeypatch.setattr(gi, "get_db", lambda: conn)
    monkeypatch.setattr(gu, "get_db", lambda: conn)
    monkeypatch.setattr(gh, "get_db", lambda: conn)
    monkeypatch.setattr(pb, "get_db", lambda: conn)


# =============================================================
#  SIMPLE mock_db (for teammate tests)
# =============================================================
@pytest.fixture
def mock_db(monkeypatch):
    """
    Simple DB mock used by teammate tests.
    cursor.fetchone → first row
    cursor.fetchall → all rows
    """

    def _patch_db(rows=None, side_effect=None):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False

        if side_effect:
            mock_cursor.execute.side_effect = side_effect
            mock_cursor.fetchone.side_effect = side_effect
            mock_cursor.fetchall.side_effect = side_effect
        else:
            mock_cursor.fetchone.return_value = rows[0] if rows else None
            mock_cursor.fetchall.return_value = rows or []

        patch_all_get_db(monkeypatch, mock_conn)
        return mock_cursor

    return _patch_db


# =============================================================
#  ADVANCED fake_db (post_weight + batch-weight tests)
# =============================================================
@pytest.fixture
def fake_db(monkeypatch):
    """
    Handles:
    ✔ get_last_weigh (dict rows)
    ✔ OUT calculation (truck tara + container weights)
    ✔ post_batch_weight upsert (no-op)
    """

    def _patch_db(rows=None, container_weights=None, last_id=1):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.commit.return_value = None

        # context manager
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = False

        fetch_sequence = []

        # --------------------------
        # fetchone → RETURNS DICTS
        # --------------------------
        def fake_fetchone():
            if not fetch_sequence:
                return None

            action = fetch_sequence.pop(0)

            # get_last_weigh()
            if action == "last":
                if rows and rows[0] is not None:
                    r = rows[0]
                    return {
                        "id": r[0],
                        "direction": r[1],
                        "session_id": r[2],
                        "bruto": r[3],
                        "datetime": r[4],
                    }
                return None

            # truck tara
            if action == "truck_tara":
                if rows and rows[0] is not None:
                    return {"bruto": rows[0][3]}
                return None

            # container weights
            if action.startswith("container:"):
                cid = action.split(":")[1]
                if container_weights and cid in container_weights:
                    return {"weight": container_weights[cid]}
                return None

            return None

        mock_cursor.fetchone.side_effect = fake_fetchone

        # --------------------------
        # SQL routing
        # --------------------------
        def fake_execute(sql, params=None):
            sql_l = sql.strip().lower()

            # get_last_weigh()
            if (
                "from transactions" in sql_l
                and "where truck" in sql_l
                and "order by datetime" in sql_l
            ):
                fetch_sequence.append("last")

            # OUT: find IN bruto
            elif (
                "from transactions" in sql_l
                and "direction='in'" in sql_l
                and "session_id" in sql_l
            ):
                fetch_sequence.append("truck_tara")

            # container lookup
            elif "select weight from containers_registered" in sql_l:
                fetch_sequence.append(f"container:{params[0]}")

            # batch-weight INSERT → no-op
            elif "insert into containers_registered" in sql_l:
                return

            # other write SQL → ignore safely
            else:
                return

        mock_cursor.execute.side_effect = fake_execute

        # lastrowid support
        type(mock_cursor).lastrowid = last_id

        # apply mock to ALL modules
        patch_all_get_db(monkeypatch, mock_conn)

        return mock_cursor

    return _patch_db
