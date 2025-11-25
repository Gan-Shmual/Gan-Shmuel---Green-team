"""
Unit tests for Truck API endpoints.
Tests the /truck POST, PUT, and GET endpoints.
"""

import json
from unittest.mock import patch, MagicMock
from flaskr.db import db
from flaskr.models.biling import Provider


def test_create_truck_success(client, sample_provider):
    """Test 6: Successfully create a new truck."""
    response = client.post('/truck',
                          json={'id': 'XYZ789', 'provider': sample_provider},
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['id'] == 'XYZ789'
    assert data['provider_id'] == sample_provider


def test_create_truck_missing_id(client, sample_provider):
    """Test 7: Create truck without ID should fail."""
    response = client.post('/truck',
                          json={'provider': sample_provider},
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_create_truck_missing_provider(client):
    """Test 8: Create truck without provider should fail."""
    response = client.post('/truck',
                          json={'id': 'ABC123'},
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_create_truck_invalid_provider(client):
    """Test 9: Create truck with non-existent provider should fail."""
    response = client.post('/truck',
                          json={'id': 'ABC123', 'provider': 99999},
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'does not exist' in data['error'].lower()


def test_create_truck_duplicate(client, sample_provider, sample_truck):
    """Test 10: Create duplicate truck should fail."""
    response = client.post('/truck',
                          json={'id': sample_truck, 'provider': sample_provider},
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'already exists' in data['error'].lower()


def test_update_truck_success(client, sample_truck, app):
    """Test 11: Successfully update a truck's provider."""
    with app.app_context():
        new_provider = Provider(name="New Provider for Truck")
        db.session.add(new_provider)
        db.session.commit()
        new_provider_id = new_provider.id
    
    response = client.put(f'/truck/{sample_truck}',
                         json={'provider': new_provider_id},
                         content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['provider_id'] == new_provider_id


def test_update_truck_not_found(client, sample_provider):
    """Test 12: Update non-existent truck should fail."""
    response = client.put('/truck/NOTEXIST',
                         json={'provider': sample_provider},
                         content_type='application/json')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data


@patch('flaskr.routes.trucks.from_weights')
def test_get_truck_success(mock_from_weights, client, sample_truck):
    """Test 13: Successfully retrieve truck information."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "id": sample_truck,
        "tara": 5000,
        "sessions": ["session1", "session2"]
    }
    mock_from_weights.return_value = mock_response
    
    response = client.get(f'/truck/{sample_truck}')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['truck_id'] == sample_truck
    assert data['tara'] == 5000
    assert len(data['sessions']) == 2


@patch('flaskr.routes.trucks.from_weights')
def test_get_truck_with_time_params(mock_from_weights, client, sample_truck):
    """Test 14: Retrieve truck with time parameters."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "id": sample_truck,
        "tara": 5000,
        "sessions": []
    }
    mock_from_weights.return_value = mock_response
    
    response = client.get(f'/truck/{sample_truck}?from=20231101000000&to=20231130235959')
    
    assert response.status_code == 200
    mock_from_weights.assert_called_once()
