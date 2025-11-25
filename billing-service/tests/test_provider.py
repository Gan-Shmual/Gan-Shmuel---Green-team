"""
Unit tests for Provider API endpoints.
Tests the /provider POST and PUT endpoints.
"""

import json
from flaskr.db import db
from flaskr.models.biling import Provider


def test_create_provider_success(client):
    """Test 1: Successfully create a new provider."""
    response = client.post('/provider',
                          json={'name': 'New Provider'},
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data
    assert isinstance(data['id'], int)


def test_create_provider_missing_name(client):
    """Test 2: Create provider without name should fail."""
    response = client.post('/provider',
                          json={},
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'required' in data['error'].lower()


def test_create_provider_duplicate_name(client, sample_provider, app):
    """Test 3: Create provider with duplicate name should fail."""
    with app.app_context():
        provider = db.session.get(Provider, sample_provider)
        provider_name = provider.name
    
    response = client.post('/provider',
                          json={'name': provider_name},
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'already exists' in data['error'].lower()


def test_update_provider_success(client, sample_provider):
    """Test 4: Successfully update a provider's name."""
    response = client.put(f'/provider/{sample_provider}',
                         json={'name': 'Updated Provider'},
                         content_type='application/json')
    
    assert response.status_code == 200


def test_update_provider_not_found(client):
    """Test 5: Update non-existent provider should fail."""
    response = client.put('/provider/99999',
                         json={'name': 'Updated Name'},
                         content_type='application/json')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
