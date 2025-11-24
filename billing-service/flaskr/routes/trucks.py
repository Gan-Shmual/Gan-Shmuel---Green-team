from flask import Blueprint, request, jsonify
from flaskr.db import db
from flaskr.models.biling import Provider, Truck
import requests

base_path="localhost:5000"
trucks = Blueprint('trucks', __name__)

@trucks.post('/truck')
def create_truck():
    data = request.get_json()
    truck_id = data.get('id')
    provider_id = data.get('provider')
    
    # Check validity
    if not truck_id:
        return jsonify({'error': 'Truck id is required'}), 400
    if not provider_id:
        return jsonify({'error': 'provider_id is required'}), 400
    provider = db.session.get(Provider, provider_id)
    if provider is None:
        return jsonify({'error': 'Provider does not exist'}), 400
    # Check truck doesn't exist 
    existing = db.session.get(Truck, truck_id)
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

@trucks.put('/truck/<id>')
def update_truck(id):
    truck = db.session.get(Truck, id)
    if truck is None:
        return jsonify({'error': 'Truck not found'}), 404
    
    data = request.get_json()
    provider_id = data.get('provider_id')
    if not provider_id:
        return jsonify({'error': 'provider_id is required'}), 400
    provider = db.session.get(Provider, provider_id)
    if provider is None:
        return jsonify({'error': 'Provider does not exist'}), 400
    # update truck
    truck.provider_id=provider.id
    db.session.commit()

    return jsonify({ 'id': truck.id, 'provider_id': truck.provider_id }), 200

@trucks.get('/truck/<truck_id>')
def get_truck(truck_id):
    t1 = request.args.get('from')
    t2 = request.args.get('to')

    response = requests.get(
        f"http://{base_path}/item/{truck_id}",
        params={"from": t1, "to": t2}
    )
    if not response.ok:
        return jsonify({"error": "Truck not found"}), response.status_code

    data = response.json()

    return jsonify({
        "truck_id": data["id"],
        "tara": data["tara"],
        "sessions": data["sessions"]
    }), 200
