def test_health_ok(client, mock_db):
    # Simulate DB returning "1" (Successful connection)
    mock_db(rows=[{"1": 1}])
    
    rv = client.get("/health")
    assert rv.status_code == 200
    assert rv.get_data(as_text=True) == "OK"

def test_health_failure(client, mock_db):
    # Simulate DB raising an exception
    mock_db(side_effect=Exception("DB connection failed"))

    rv = client.get("/health")
    assert rv.status_code == 500
    assert rv.get_data(as_text=True) == "Failure"