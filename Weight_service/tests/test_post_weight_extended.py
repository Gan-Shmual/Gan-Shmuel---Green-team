import pytest
from unittest.mock import ANY
from Routes.post_weight import (
    validate_direction_rules,
    get_last_weigh,
)

# ============================================================
#  A. DIRECTION RULE LOGIC
# ============================================================

def test_rule_out_without_in():
    error = validate_direction_rules("out", None, False)
    assert error == "OUT without a previous IN is not allowed"


def test_rule_none_after_in():
    last = {"direction": "in"}
    error = validate_direction_rules("none", last, False)
    assert error == "NONE after IN is not allowed"


def test_rule_in_after_in_without_force():
    last = {"direction": "in"}
    error = validate_direction_rules("in", last, False)
    assert error == "IN after IN requires force=true"


def test_rule_in_after_in_with_force():
    last = {"direction": "in"}
    error = validate_direction_rules("in", last, True)
    assert error is None


def test_rule_out_normal():
    last = {"direction": "in"}
    error = validate_direction_rules("out", last, False)
    assert error is None


# ============================================================
#  B. DB HELPERS (mock DB)
# ============================================================

def test_get_last_weigh_found(fake_db):
    fake_db(rows=[(5, "in", 10, 1200, "20240101120000")])
    from Routes import post_weight as pw
    result = pw.get_last_weigh("123")

    assert result["id"] == 5
    assert result["direction"] == "in"
    assert result["session_id"] == 10
    assert result["bruto"] == 1200


def test_get_last_weigh_none(fake_db):
    fake_db(rows=[None])
    from Routes import post_weight as pw
    result = pw.get_last_weigh("x")
    assert result is None


def test_save_transaction_insert(fake_db):
    """
    Should call INSERT when no last_weigh exists.
    """
    cursor = fake_db(rows=[None], last_id=99)

    from Routes import post_weight as pw
    tx_id = pw.save_transaction(
        "in", "123", ["a"], 100, "orange", None, None, True
    )

    assert tx_id == 99

    # Check INSERT query was executed
    calls = [str(c) for c in cursor.execute.call_args_list]
    assert any("insert into transactions" in c.lower() for c in calls)

    # Check parameters
    cursor.execute.assert_any_call(
        ANY,
        ("in", "123", "a", 100, "orange", None)
    )


def test_save_transaction_update(fake_db):
    """
    Should call UPDATE when same direction + force.
    """
    last = {"id": 5, "direction": "in"}
    cursor = fake_db(rows=[None], last_id=5)

    from Routes import post_weight as pw
    tx_id = pw.save_transaction(
        "in", "123", ["a"], 100, "orange", None, last, True
    )

    assert tx_id == 5

    # Check UPDATE query was executed
    calls = [str(c) for c in cursor.execute.call_args_list]
    assert any("update transactions" in c.lower() for c in calls)

    cursor.execute.assert_any_call(
        ANY,
        ("in", "123", "a", 100, "orange", 5)
    )


def test_calculate_out_values_basic(fake_db):
    cursor = fake_db(
        rows=[(1, "in", 1, 900, "2024")],
        container_weights={"a": 10, "b": 5},
    )

    from Routes import post_weight as pw
    truck_tara, neto = pw.calculate_out_values(20, 1, ["a", "b"], 1200)

    assert truck_tara == 900
    assert neto == 1200 - 900 - (10 + 5)


# ============================================================
#  C. POST /WEIGHT ENDPOINT TESTS
# ============================================================

def test_post_weight_missing_fields(client):
    resp = client.post("/weight", json={"direction": "in"})
    assert resp.status_code == 400


def test_post_weight_invalid_unit(client):
    payload = {
        "direction": "in",
        "truck": "123",
        "containers": "x",
        "weight": "100",
        "unit": "stone",
        "force": "true",
        "produce": "orange"
    }
    resp = client.post("/weight", json=payload)
    assert resp.status_code == 400


def test_post_weight_invalid_force(client):
    payload = {
        "direction": "in",
        "truck": "123",
        "containers": "x",
        "weight": "100",
        "unit": "kg",
        "force": "maybe",
        "produce": "orange"
    }
    resp = client.post("/weight", json=payload)
    assert resp.status_code == 400


def test_post_weight_negative_weight(client):
    payload = {
        "direction": "in",
        "truck": "123",
        "containers": "x",
        "weight": "-10",
        "unit": "kg",
        "force": "true",
        "produce": "orange"
    }
    resp = client.post("/weight", json=payload)
    assert resp.status_code == 400


def test_post_weight_non_integer_weight(client):
    payload = {
        "direction": "in",
        "truck": "123",
        "containers": "x",
        "weight": "10.5",
        "unit": "kg",
        "force": "true",
        "produce": "orange"
    }
    resp = client.post("/weight", json=payload)
    assert resp.status_code == 400


def test_post_weight_in_after_in_without_force(client, fake_db):
    fake_db(rows=[("id", "in", 10, 900, "2024")])
    payload = {
        "direction": "in",
        "truck": "123",
        "containers": "x",
        "weight": "100",
        "unit": "kg",
        "force": "false",
        "produce": "orange"
    }
    resp = client.post("/weight", json=payload)
    assert resp.status_code == 400


def test_post_weight_simple_out_with_known_containers(client, fake_db):
    fake_db(
        rows=[(1, "in", 1, 900, "2024")],
        container_weights={"a": 10},
        last_id=2
    )

    payload = {
        "direction": "out",
        "truck": "123",
        "containers": "a",
        "weight": "1200",
        "unit": "kg",
        "force": "true",
        "produce": "orange"
    }

    resp = client.post("/weight", json=payload)
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["truckTara"] == 900
    assert data["neto"] == 1200 - 900 - 10
