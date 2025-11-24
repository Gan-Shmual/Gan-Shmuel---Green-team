from flask import Flask
# FIX: Import directly from Routes
from Routes.get_health import get_health_bp
from Routes.post_weight import post_weight_bp
from Routes.get_weight import get_weight_bp
from Routes.get_item import get_item_bp
from Routes.post_batch_weight import post_batch_bp
from Routes.get_unknown import get_unknown_bp

app = Flask(__name__)

app.register_blueprint(get_health_bp) 
app.register_blueprint(get_weight_bp)
app.register_blueprint(post_weight_bp)
app.register_blueprint(get_item_bp)
app.register_blueprint(post_batch_bp)
app.register_blueprint(get_unknown_bp)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)