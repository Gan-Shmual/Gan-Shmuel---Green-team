from flask import Flask
from Routes.get_health import get_health_bp
from Routes.post_weight import post_weight_bp
from Routes.get_weight import get_weight_bp


app = Flask(__name__)

# Register each blueprint separately
app.register_blueprint(get_health_bp)
app.register_blueprint(get_weight_bp)
app.register_blueprint(post_weight_bp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)