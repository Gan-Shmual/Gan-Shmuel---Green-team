from flask import Blueprint, request, jsonify
from flaskr.db import db
from flaskr.models.biling import Provider, Truck, Rate

bp = Blueprint('main', __name__)

#General
@bp.route('/health')
def health():
    return "ok";

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

@bp.post('/truck')
def create_truck():
    data = request.get_json()
    truck_id = data.get('id')
    provider_id = data.get('provider_id')
    
    # Check validity
    if not truck_id:
        return jsonify({'error': 'Truck id is required'}), 400
    if not provider_id:
        return jsonify({'error': 'provider_id is required'}), 400
    # Check provider exists
    provider = Provider.query.get(provider_id)
    if provider is None:
        return jsonify({'error': 'Provider does not exist'}), 400
    # Check truck doesn't exist 
    existing = Truck.query.filter_by(id=truck_id).first()
    if existing:
        return jsonify({'error': 'Truck already exists'}), 400
    # add truck
    new_truck = Truck(
        id=truck_id,
        provider_id=provider.id
    )
    db.session.add(new_truck)
    db.session.commit()

    return jsonify({ 'id': new_truck.id,
        'provider_id': new_truck.provider_id }), 201

@bp.put('/truck/{id}')
def update_truck(provider_id):
    data = request.get_json()
    truck_id = data.get('id')
    provider_id = data.get('provider_id')
    
    # Check validity
    if not truck_id:
        return jsonify({'error': 'Truck id is required'}), 400
    if not provider_id:
        return jsonify({'error': 'provider_id is required'}), 400
    # Check provider exists
    provider = Provider.query.get(provider_id)
    if provider is None:
        return jsonify({'error': 'Provider does not exist'}), 400
    # Check truck exist 
    existing = Truck.query.filter_by(id=truck_id).first()
    if existing:
        return jsonify({'error': 'Truck already exists'}), 400
    # add truck
    new_truck = Truck(
        id=truck_id,
        provider_id=provider.id
    )
    db.session.add(new_truck)
    db.session.commit()

    return jsonify({ 'id': new_truck.id,
        'provider_id': new_truck.provider_id }), 201