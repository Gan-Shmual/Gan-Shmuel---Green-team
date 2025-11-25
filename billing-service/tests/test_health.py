"""
Unit tests for Health Check endpoint.
Tests the /health GET endpoint.
"""


def test_health_check(client):
    """Test: Health check endpoint should return OK."""
    response = client.get('/health')
    
    assert response.status_code == 200
    assert response.data == b'ok'
