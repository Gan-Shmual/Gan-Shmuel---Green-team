from flask import Blueprint

# Create a Blueprint for the API
# The url_prefix will be prepended to all routes in this blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import all the route functions from your Routes directory
# and register them with the blueprint
from Routes.get_health import get_health
from Routes.get_item import get_item
from Routes.get_session import get_session
from Routes.get_unknown import get_unknown
from Routes.get_weight import get_weight
from Routes.post_batch_weight import post_batch_weight
from Routes.post_weight import post_weight

# Register the routes with the blueprint
# The first argument is the function, the second is the rule (URL), and the third is the method
api_bp.add_url_rule('/health', 'health', get_health, methods=['GET'])
api_bp.add_url_rule('/item/<id>', 'get_item', get_item, methods=['GET'])
api_bp.add_url_rule('/session/<id>', 'get_session', get_session, methods=['GET'])
api_bp.add_url_rule('/unknown', 'get_unknown', get_unknown, methods=['GET'])
api_bp.add_url_rule('/weight', 'get_weight', get_weight, methods=['GET'])
api_bp.add_url_rule('/batch-weight', 'post_batch_weight', post_batch_weight, methods=['POST'])
api_bp.add_url_rule('/weight', 'post_weight', post_weight, methods=['POST'])