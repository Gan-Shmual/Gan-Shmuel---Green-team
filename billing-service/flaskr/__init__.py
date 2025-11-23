import os
from flaskr.routes import main
from flaskr.routes import trucks
from flaskr.routes import rates
from flask import Flask
from flaskr.db import db, init_db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load settings from instance/settings.py
    app.config.from_pyfile('settings.py')

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    init_db(app)

    with app.app_context():
        db.create_all()

    # register blueprints
    app.register_blueprint(main.bp)
    app.register_blueprint(trucks.trucks)
    app.register_blueprint(rates.rates)

    return app
