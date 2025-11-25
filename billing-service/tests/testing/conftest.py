"""
Shared pytest fixtures for billing service tests.
"""

import sys
import os

# Add parent directory to path so we can import flaskr
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from flaskr import create_app
from flaskr.db import db
from flaskr.models.biling import Provider, Truck, Rate


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    from flask import Flask
    from flaskr.routes import main, trucks, bill, rates, provider
    from flaskr.routes.ui_routes import ui_bp
    
    # Create app directly without loading settings.py
    app = Flask(__name__)
    
    # Configure for testing with SQLite
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'WEIGHTS_URL': 'http://localhost:6000'  # Mock weight service
    })
    
    # Initialize db directly without init_db (which overrides our config)
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(ui_bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(trucks.trucks)
    app.register_blueprint(bill.bill)
    app.register_blueprint(rates.rates)
    app.register_blueprint(provider.provider)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the application."""
    return app.test_client()


@pytest.fixture
def sample_provider(app):
    """Create a sample provider in the database."""
    with app.app_context():
        provider = Provider(name="Test Provider")
        db.session.add(provider)
        db.session.commit()
        provider_id = provider.id
    return provider_id


@pytest.fixture
def sample_truck(app, sample_provider):
    """Create a sample truck in the database."""
    with app.app_context():
        truck = Truck(id="ABC123", provider_id=sample_provider)
        db.session.add(truck)
        db.session.commit()
        truck_id = truck.id
    return truck_id


@pytest.fixture
def sample_rates(app, sample_provider):
    """Create sample rates in the database."""
    with app.app_context():
        rates = [
            Rate(product_id="orange", rate=500, scope="ALL"),
            Rate(product_id="tomato", rate=300, scope="ALL"),
            Rate(product_id="apple", rate=450, scope=str(sample_provider))
        ]
        for rate in rates:
            db.session.add(rate)
        db.session.commit()
