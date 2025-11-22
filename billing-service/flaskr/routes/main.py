from flask import Blueprint, request, jsonify
from flaskr.db import db
from flaskr.models.biling import Provider

bp = Blueprint('main', __name__)

#General
@bp.route('/health')
def health():
    return "ok"

#Providers
@bp.post('/provider')
def create_provider():
    data = request.get_json()
    provider_name = data.get('name')
    if provider_name == None:
        return jsonify({'error': 'Provider name is required'}), 400
    existing = Provider.query.filter_by(name=provider_name).first()
    if existing:
        return jsonify({'error': 'Provider already exists'}), 400
    new_provider = Provider(name=provider_name)
    db.session.add(new_provider)
    db.session.commit()
    return jsonify({'id': new_provider.id}), 201

@bp.put('/provider/{id}')
def update_provider(provider_id):
    data = request.get_json()
    new_name = data.get('name')
    if new_name == None:
        return jsonify({'error': 'Provider name is required'}), 400
    provider = Provider.query.get(provider_id)
    if not provider:
        return jsonify({'error': 'Provider not found'}), 404
    provider.name = new_name
    db.session.commit()

