# Billing Service Unit Tests

This directory contains comprehensive pytest unit tests for the Billing Service API.

## Test Structure

The tests are organized into separate modules by functionality:

- **`conftest.py`** - Shared pytest fixtures and test configuration
- **`test_provider.py`** - Tests for Provider API endpoints (5 tests)
- **`test_truck.py`** - Tests for Truck API endpoints (9 tests)
- **`test_rates.py`** - Tests for Rates API endpoints (4 tests)
- **`test_bill.py`** - Tests for Bill API endpoints (2 tests)
- **`test_health.py`** - Tests for Health Check endpoint (1 test)

**Total: 21 unit tests**

## Running Tests

### Run all tests:
```bash
pytest testing/
```

### Run tests with verbose output:
```bash
pytest testing/ -v
```

### Run specific test file:
```bash
pytest testing/test_provider.py -v
```

### Run with coverage:
```bash
pytest testing/ --cov=flaskr --cov-report=html
```

## Test Coverage

### Provider Endpoints (`POST /provider`, `PUT /provider/<id>`)
- ✅ Create provider successfully
- ✅ Create provider without name (validation)
- ✅ Create provider with duplicate name (validation)
- ✅ Update provider successfully
- ✅ Update non-existent provider (404)

### Truck Endpoints (`POST /truck`, `PUT /truck/<id>`, `GET /truck/<id>`)
- ✅ Create truck successfully
- ✅ Create truck without ID (validation)
- ✅ Create truck without provider (validation)
- ✅ Create truck with invalid provider (validation)
- ✅ Create duplicate truck (validation)
- ✅ Update truck successfully
- ✅ Update non-existent truck (404)
- ✅ Get truck information successfully (mocked weight service)
- ✅ Get truck with time parameters

### Rates Endpoints (`POST /rates`, `GET /rates`)
- ✅ Upload rates from Excel successfully
- ✅ Upload rates with non-existent file (404)
- ✅ Download rates successfully
- ✅ Download rates when no file exists (404)

### Bill Endpoint (`GET /bill/<id>`)
- ✅ Generate bill for provider successfully (mocked weight service)
- ✅ Generate bill for non-existent provider (404)

### Health Endpoint (`GET /health`)
- ✅ Health check returns OK

## Fixtures

The `conftest.py` file provides reusable fixtures:

- **`app`** - Test Flask application instance with in-memory SQLite database
- **`client`** - Test client for making HTTP requests
- **`sample_provider`** - Pre-created provider for testing
- **`sample_truck`** - Pre-created truck for testing
- **`sample_rates`** - Pre-created rates for testing

## Mocking

Tests use `unittest.mock` to mock external dependencies:
- Weight service calls (`from_weights`)
- File system operations
- Excel file operations

## Requirements

Make sure pytest and pytest-mock are installed (already in `requirements.txt`):
```bash
pip install -r requirements.txt
```
