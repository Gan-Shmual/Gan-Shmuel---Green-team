"""
Unit tests for Bill API endpoints.
Tests the /bill GET endpoint.
"""

import json
from unittest.mock import patch, MagicMock


@patch('flaskr.routes.bill.from_weights')
def test_get_bill_success(mock_from_weights, client, app, sample_provider, sample_truck, sample_rates):
    """Test 19: Successfully generate bill for a provider."""
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "truck": sample_truck,
            "neto": 1000,
            "produce": "orange"
        },
        {
            "truck": sample_truck,
            "neto": 500,
            "produce": "tomato"
        }
    ]
    mock_from_weights.return_value = mock_response
    
    response = client.get(f'/bill/{sample_provider}?from=20231101000000&to=20231130235959')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == str(sample_provider)
    assert 'name' in data
    assert data['truckCount'] == 1
    assert data['sessionCount'] == 2
    assert len(data['products']) == 2
    assert data['total'] > 0


@patch('flaskr.routes.bill.from_weights')
def test_get_bill_provider_not_found(mock_from_weights, client):
    """Test 20: Generate bill for non-existent provider should fail."""
    response = client.get('/bill/99999?from=20231101000000&to=20231130235959')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
