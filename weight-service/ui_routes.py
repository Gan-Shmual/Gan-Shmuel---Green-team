from flask import Blueprint, render_template, request, redirect, url_for

# Create a Blueprint for the UI
ui_bp = Blueprint('ui', __name__)

# Define all the UI routes
@ui_bp.route('/')
def index():
    """Redirects to the weight form page."""
    return redirect(url_for('ui.weight_form'))

@ui_bp.route('/weight-form')
def weight_form():
    """Renders the weight recording form."""
    container_id = request.args.get('container', '')
    return render_template('weight_form.html', container_id=container_id)

@ui_bp.route('/batch-weight')
def batch_weight():
    """Renders the batch weight upload page."""
    return render_template('batch_weight.html')

@ui_bp.route('/unknown-containers')
def unknown_containers():
    """Renders the page listing containers with unknown weights."""
    return render_template('unknown.html')

@ui_bp.route('/weight-history')
def weight_history():
    """Renders the weight history page."""
    return render_template('weight_history.html')

@ui_bp.route('/item-details')
def item_details():
    """Renders the item details page."""
    return render_template('item.html')

@ui_bp.route('/session-details')
def session_details():
    """Renders the session details page."""
    return render_template('session.html')

@ui_bp.route('/health-status')
def health_status():
    """Renders the system health status page."""
    return render_template('health.html')