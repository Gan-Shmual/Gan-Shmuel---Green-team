from flask import Flask
import os

def create_app():
    """Application factory pattern."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register the API Blueprint
    import api_routes
    app.register_blueprint(api_routes.api_bp)

    # Register the UI Blueprint
    import ui_routes
    app.register_blueprint(ui_routes.ui_bp)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app

# This part is for running the app directly with `python app.py`
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
