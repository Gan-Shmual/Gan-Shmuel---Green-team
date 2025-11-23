from flask import Blueprint, request, jsonify
from flaskr.db import db
from flaskr.models.biling import Provider, Truck
from flaskr.wights import from_wights

bill = Blueprint('bill', __name__)

#/bill/?from=t1&to=t2
@bill.route('/bill/<id>')
def get_bill(id):
    from_time = request.args.get('from')
    to_time = request.args.get('to')
    if not from_time or not to_time:
        return jsonify({'error': 'from and to parameters are required'}), 400
    try:
        wight_item = from_wights(f'wight{id}', {'from': from_time, 'to': to_time})
        provider = db.session.get(Provider, id)
        res = {
            "id": id,
            "name": provider.name if provider else None,
            "from": from_time,
            "to": to_time,
            "truckCount": db.session.query(Truck).filter_by(provider_id=provider.id).count(),
            "sessionCount": "",
            "products": "" #bytruck
              }
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(res), 200


