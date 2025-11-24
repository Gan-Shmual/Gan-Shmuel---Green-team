def test_health_ok(client, fake_db_connection):
    # Setup a fake DB that returns at least one result for SELECT 1;
    fake_db_connection(rows=[{"1": 1}])
    rv = client.get("/health")
    assert rv.status_code == 200
    assert rv.get_data(as_text=True) == "OK"

def test_health_failure(client, monkeypatch):
    # Patch get_db to raise an exception to simulate DB down
    import db as db_module
    def raise_exc():
        raise Exception("db down")
    monkeypatch.setattr(db_module, "get_db", raise_exc)

    rv = client.get("/health")
    assert rv.status_code == 500
    assert rv.get_data(as_text=True) == "Failure"
