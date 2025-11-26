"""
Unit tests for Rates API endpoints.
Tests the /rates POST and GET endpoints.
"""

import json
from unittest.mock import patch, MagicMock
import pandas as pd


@patch('flaskr.routes.rates.db.session.execute')
@patch('flaskr.routes.rates.db.session.bulk_insert_mappings')
@patch('flaskr.routes.rates.db.session.commit')
@patch('flaskr.routes.rates.os.path.exists')
@patch('flaskr.routes.rates.pd.read_excel')
@patch('flaskr.routes.rates.pd.DataFrame.to_excel')
def test_upload_rates_success(mock_to_excel, mock_read_excel, mock_exists, mock_commit, mock_bulk_insert, mock_execute, client, app):
    """Test 15: Successfully upload rates from Excel file."""
    mock_exists.return_value = True
    mock_df = pd.DataFrame({
        'Product': ['orange', 'tomato'],
        'Rate': [500, 300],
        'Scope': ['ALL', 'ALL']
    })
    mock_read_excel.return_value = mock_df
    
    response = client.post('/rates',
                          json={'filename': 'rates.xlsx'},
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    # Verify that TRUNCATE was called
    mock_execute.assert_called_once()
    # Verify bulk insert was called
    mock_bulk_insert.assert_called_once()


@patch('flaskr.routes.rates.os.path.exists')
def test_upload_rates_file_not_found(mock_exists, client):
    """Test 16: Upload rates with non-existent file should fail."""
    mock_exists.return_value = False
    
    response = client.post('/rates',
                          json={'filename': 'nonexistent.xlsx'},
                          content_type='application/json')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data


@patch('flaskr.routes.rates.os.path.exists')
@patch('flaskr.routes.rates.send_file')
def test_download_rates_success(mock_send_file, mock_exists, client):
    """Test 17: Successfully download rates file."""
    mock_exists.return_value = True
    mock_send_file.return_value = MagicMock()
    
    response = client.get('/rates')
    
    assert response.status_code == 200
    mock_send_file.assert_called_once()


@patch('flaskr.routes.rates.os.path.exists')
def test_download_rates_no_file(mock_exists, client):
    """Test 18: Download rates when no file uploaded should fail."""
    mock_exists.return_value = False
    
    response = client.get('/rates')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
