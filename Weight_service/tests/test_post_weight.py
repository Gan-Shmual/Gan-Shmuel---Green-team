import pytest
from Routes.post_weight import (
    validate_required_fields,
    parse_force,
    parse_containers,
    normalize_input,
    convert_to_kg,
    validate_direction_rules,
    get_last_weigh,
)
from flask import json


# --------------------------
#  VALIDATION UTILITIES TESTS
# --------------------------

def test_required_fields_missing():
    data = {"truck": "123", "weight": 100}
    missing = validate_required_fields(data)
    assert "direction" in missing
    assert "containers" in missing
    assert "unit" in missing


def test_parse_force():
    assert parse_force(True) is True
    assert parse_force("true") is True
    assert parse_force("1") is True
    assert parse_force("yes") is True

    assert parse_force(False) is False
    assert parse_force("false") is False
    assert parse_force("0") is False
    assert parse_force("no") is False

    assert parse_force("maybe") is None
    assert parse_force(None) is None


def test_parse_containers():
    assert parse_containers("a,b,c") == ["a", "b", "c"]
    assert parse_containers(["x", "y"]) == ["x", "y"]
    assert parse_containers("   x ,  y  ") == ["x", "y"]


def test_normalize_input():
    data = {
        "direction": "IN ",
        "truck": " 1234 ",
        "produce": " TOMATO ",
        "unit": " KG "
    }
    direction, truck, produce, unit = normalize_input(data)
    assert direction == "in"
    assert truck == "1234"
    assert produce == "tomato"
    assert unit == "kg"


def test_convert_to_kg():
    assert convert_to_kg(100, "kg") == 100
    assert convert_to_kg(100, "lbs") == 45  # rounded


# --------------------------
#  DIRECTION LOGIC
# --------------------------

def test_direction_rules_no_previous_out():
    error = validate_direction_rules("out", None, False)
    assert error == "OUT without a previous IN is not allowed"


def test_direction_rules_in_after_in_without_force():
    last = {"direction": "in"}
    error = validate_direction_rules("in", last, False)
    assert error == "IN after IN requires force=true"


def test_direction_rules_in_after_in_with_force():
    last = {"direction": "in"}
    error = validate_direction_rules("in", last, True)
    assert error is None


# --------------------------
#  ENDPOINT TESTS
# --------------------------

def test_post_weight_happy_in(client, fake_db):
    """
    Test a basic IN request that inserts a new record.
    """

    # Step 1: mock DB get_last_weigh → return None (first time)
    fake_db(rows=[None], last_id=10)  # get_last_weigh returns None

    payload = {
        "direction": "in",
        "truck": "123",
        "containers": "a,b",
        "weight": "100",
        "unit": "kg",
        "force": "true",
        "produce": "orange"
    }

    resp = client.post("/weight", json=payload)
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["truck"] == "123"
    assert data["bruto"] == 100


def test_post_weight_invalid_direction(client):
    payload = {
        "direction": "sideways",
        "truck": "123",
        "containers": "a",
        "weight": "100",
        "unit": "kg",
        "force": "true",
        "produce": "orange"
    }

    resp = client.post("/weight", json=payload)
    assert resp.status_code == 400
    assert "invalid direction" in resp.get_data(as_text=True)
