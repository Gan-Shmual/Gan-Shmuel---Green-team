import pytest
import json
import os
import builtins
from Routes.post_batch_weight import (
    convert_unit,
    process_csv,
    process_json
)

# =====================================================
# UNIT: convert_unit
# =====================================================

def test_convert_unit_kg():
    assert convert_unit(100, "kg") == 100


def test_convert_unit_lbs():
    assert convert_unit(100, "lbs") == 45


def test_convert_unit_invalid():
    with pytest.raises(ValueError):
        convert_unit(10, "stone")

# =====================================================
# UNIT: process_csv
# =====================================================

def test_process_csv_basic(tmp_path, fake_db):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("id,weight,unit\na,100,kg\nb,50,lbs\n")

    fake_db(rows=[None], last_id=1)

    processed, errors = process_csv(str(csv_file))

    assert processed == 2
    assert errors == []


def test_process_csv_null_weights(tmp_path, fake_db):
    csv_file = tmp_path / "nulls.csv"
    csv_file.write_text("id,weight\na,null\nb,NA\n")

    fake_db(rows=[None], last_id=1)

    processed, errors = process_csv(str(csv_file))

    assert processed == 2
    assert len(errors) == 2


def test_process_csv_invalid_row(tmp_path, fake_db):
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text("id,weight\na,notnumber\n")

    fake_db(rows=[None], last_id=1)

    processed, errors = process_csv(str(csv_file))

    assert processed == 0
    assert len(errors) == 1

# =====================================================
# UNIT: process_json
# =====================================================

def test_process_json_basic(tmp_path, fake_db):
    jfile = tmp_path / "test.json"
    jfile.write_text(json.dumps([
        {"id": "a", "weight": 100, "unit": "kg"},
        {"id": "b", "weight": 50, "unit": "lbs"}
    ]))

    fake_db(rows=[None], last_id=1)

    processed, errors = process_json(str(jfile))

    assert processed == 2
    assert errors == []


def test_process_json_null(tmp_path, fake_db):
    jfile = tmp_path / "null.json"
    jfile.write_text(json.dumps([
        {"id": "a", "weight": None},
        {"id": "b", "weight": "null"},
    ]))

    fake_db(rows=[None], last_id=1)

    processed, errors = process_json(str(jfile))

    assert processed == 2
    assert len(errors) == 2


def test_process_json_invalid_value(tmp_path, fake_db):
    jfile = tmp_path / "invalid.json"
    jfile.write_text(json.dumps([
        {"id": "a", "weight": "bad"},
    ]))

    fake_db(rows=[None], last_id=1)

    processed, errors = process_json(str(jfile))

    assert processed == 0
    assert len(errors) == 1


def test_process_json_must_be_list(tmp_path, fake_db):
    jfile = tmp_path / "bad.json"
    jfile.write_text(json.dumps({"no": "list"}))

    with pytest.raises(ValueError):
        process_json(str(jfile))

# =====================================================
# ENDPOINT TESTS
# =====================================================

def test_batch_weight_missing_field(client):
    resp = client.post("/batch-weight", json={})
    assert resp.status_code == 400


def test_batch_weight_file_not_found(client):
    resp = client.post("/batch-weight", json={"file": "x.csv"})
    assert resp.status_code == 404


def test_batch_weight_unsupported_extension(client):
    resp = client.post("/batch-weight", json={"file": "abc.txt"})
    assert resp.status_code == 400


def test_batch_weight_csv_flow(client, tmp_path, fake_db, monkeypatch):
    import builtins

    csv_file = tmp_path / "a.csv"
    csv_file.write_text("id,weight\na,100\n")

    fake_db(rows=[None], last_id=1)

    # Pretend /app/in/a.csv exists
    monkeypatch.setattr(os.path, "isfile", lambda p: p == "/app/in/a.csv")

    # Save real open before patching
    real_open = builtins.open

    def fake_open(path, mode='r', encoding=None):
        if path == "/app/in/a.csv":
            return real_open(str(csv_file), mode, encoding=encoding)
        return real_open(path, mode, encoding=encoding)

    monkeypatch.setattr(builtins, "open", fake_open)

    resp = client.post("/batch-weight", json={"file": "a.csv"})
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["processed"] == 1



def test_batch_weight_json_flow(client, tmp_path, fake_db, monkeypatch):
    import builtins
    import os
    import json

    # Create a fake JSON file in tmp_path
    json_file = tmp_path / "b.json"
    json_file.write_text(json.dumps([{"id": "x", "weight": 100}]))

    fake_db(rows=[None], last_id=1)

    # Simulate that `/app/in/b.json` EXISTS
    monkeypatch.setattr(os.path, "isfile", lambda p: p == "/app/in/b.json")

    # Store the real open BEFORE monkeypatching
    real_open = builtins.open

    # Provide a safe wrapper (no recursion)
    def fake_open(path, mode="r", encoding=None):
        if path == "/app/in/b.json":
            return real_open(str(json_file), mode, encoding=encoding)
        return real_open(path, mode, encoding=encoding)

    monkeypatch.setattr(builtins, "open", fake_open)

    # Call endpoint
    resp = client.post("/batch-weight", json={"file": "b.json"})
    data = resp.get_json()

    # Assertions
    assert resp.status_code == 200
    assert data["processed"] == 1

