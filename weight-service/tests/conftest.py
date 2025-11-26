# import pytest
# from unittest.mock import Mock, MagicMock, patch
# from app import app
# from datetime import datetime
# from flask import Flask

# @pytest.fixture
# def client():
#     """Create a test client for the Flask app"""
#     app.config['TESTING'] = True
#     with app.test_client() as client:
#         yield client

# @pytest.fixture
# def mock_db():
#     """Mock database connection and cursor"""
#     mock_conn = MagicMock()
#     mock_cursor = MagicMock()
    
#     # Setup context manager for cursor
#     mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
#     mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
    
#     return mock_conn, mock_cursor

# @pytest.fixture
# def mock_get_db(mock_db):
#     """Patch the get_db function in all route modules"""
#     patches = [
#         patch('Routes.get_health.get_db'),
#         patch('Routes.get_item.get_db'),
#         patch('Routes.get_weight.get_db'),
#         patch('Routes.get_session.get_db'),
#         patch('Routes.get_unknown.get_db'),
#         patch('Routes.post_weight.get_db'),
#         patch('Routes.post_batch_weight.get_db'),
#     ]
    
#     mocks = [p.start() for p in patches]
#     for mock in mocks:
#         mock.return_value = mock_db[0]
    
#     yield mocks[0]  # Return one mock for compatibility
    
#     for p in patches:
#         p.stop()


# @pytest.fixture
# def sample_datetime():
#     """Provide a consistent datetime for testing"""
#     return datetime(2024, 1, 15, 10, 30, 0)

# @pytest.fixture
# def mock_datetime(sample_datetime):
#     """Mock datetime.now() for consistent testing"""
#     with patch('Routes.get_weight.datetime') as mock_dt:
#         mock_dt.now.return_value = sample_datetime
#         mock_dt.strptime = datetime.strptime
#         yield mock_dt

# @pytest.fixture
# def mock_datetime_item(sample_datetime):
#     """Mock datetime.now() for get_item route"""
#     with patch('Routes.get_item.datetime') as mock_dt:
#         mock_dt.now.return_value = sample_datetime
#         mock_dt.strptime = datetime.strptime
#         yield mock_dt
