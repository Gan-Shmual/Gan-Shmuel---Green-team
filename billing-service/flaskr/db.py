"""Database configuration and initialization using SQLAlchemy."""
import os
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()


def init_db(app):
    """Initialize the database with the Flask app."""
    # Construct MySQL connection string from environment variables
    db_user = app.config.get('DB_USER')
    db_password = app.config.get('DB_PASSWORD')
    db_host = app.config.get('DB_HOST')
    db_port = app.config.get('DB_PORT')
    db_name = app.config.get('DB_NAME')
    
    # Set SQLAlchemy database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    )
    
    # Disable SQLAlchemy event system (optional, improves performance)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize the database with the app
    db.init_app(app)
    
    return db
