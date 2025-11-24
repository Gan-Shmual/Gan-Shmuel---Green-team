from flask import Blueprint, request, jsonify
from flaskr.db import db
from flaskr.models.biling import Provider, Truck, Rate
from flaskr.weights import from_weights
from datetime import datetime

bill = Blueprint('bill', __name__)


def get_default_times():
    """Generate default from/to times according to API spec."""
    now = datetime.now()
    # Default from: 1st of month at 000000
    from_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Default to: now
    to_time = now
    
    return from_time.strftime('%Y%m%d%H%M%S'), to_time.strftime('%Y%m%d%H%M%S')


def get_rate_for_product(product, provider_id):
    """Get rate for a product, checking provider-specific rate first, then ALL."""
    # Check for provider-specific rate first
    provider_rate = db.session.query(Rate).filter_by(
        product_id=product,
        scope=str(provider_id)
    ).first()
    
    if provider_rate:
        return provider_rate.rate
    
    # Fall back to ALL rate
    all_rate = db.session.query(Rate).filter_by(
        product_id=product,
        scope='ALL'
    ).first()
    
    return all_rate.rate if all_rate else 0


@bill.route('/bill/<id>')
def get_bill(id):
    """Generate bill for a provider for a given time period."""
    # Get time parameters with defaults
    from_time = request.args.get('from')
    to_time = request.args.get('to')
    
    if not from_time or not to_time:
        from_time, to_time = get_default_times()
    
    try:
        # Get provider from database
        provider = db.session.get(Provider, id)
        if not provider:
            return jsonify({'error': 'Provider not found'}), 404
        
        # Get all trucks for this provider
        trucks = db.session.query(Truck).filter_by(provider_id=provider.id).all()
        truck_ids = [truck.id for truck in trucks]
        
        if not truck_ids:
            # No trucks, return empty bill
            return jsonify({
                "id": str(id),
                "name": provider.name,
                "from": from_time,
                "to": to_time,
                "truckCount": 0,
                "sessionCount": 0,
                "products": [],
                "total": 0
            }), 200
        
        # Get all weighing data from weight service
        weight_data = from_weights('weight', {
            'from': from_time,
            'to': to_time,
            'filter': 'out'  # Only completed sessions
        })
        
        # Filter sessions for this provider's trucks and aggregate by product
        products_dict = {}
        session_count = 0
        
        for session in weight_data:
            truck_id = session.get('truck')
            
            # Skip if not this provider's truck
            if truck_id not in truck_ids:
                continue
            
            # Skip if neto is "na" (unknown container weights)
            neto = session.get('neto')
            if neto == 'na' or neto is None:
                continue
            
            produce = session.get('produce')
            if not produce or produce == 'na':
                continue
            
            session_count += 1
            
            # Aggregate by product
            if produce not in products_dict:
                products_dict[produce] = {
                    'count': 0,
                    'amount': 0
                }
            
            products_dict[produce]['count'] += 1
            products_dict[produce]['amount'] += int(neto)
        
        # Build products array with rates and payments
        products = []
        total_pay = 0
        
        for product, data in products_dict.items():
            rate = get_rate_for_product(product, provider.id)
            pay = data['amount'] * rate
            total_pay += pay
            
            products.append({
                'product': product,
                'count': str(data['count']),  # API spec says string
                'amount': data['amount'],
                'rate': rate,
                'pay': pay
            })
        
        # Sort products by name for consistent output
        products.sort(key=lambda x: x['product'])
        
        # Build response
        res = {
            "id": str(id),
            "name": provider.name,
            "from": from_time,
            "to": to_time,
            "truckCount": len(trucks),
            "sessionCount": session_count,
            "products": products,
            "total": total_pay
        }
        
        return jsonify(res), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


