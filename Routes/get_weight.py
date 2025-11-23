from flask import Blueprint, request, jsonify
from db import get_db
from datetime import datetime

get_weight_bp = Blueprint("get_weight", __name__)

@get_weight_bp.route("/weight", methods=["GET"])
def get_weight():
    # 1. Get parameters
    t1 = request.args.get('t1')
    t2 = request.args.get('t2')
    filter_param = request.args.get('filter', 'in,out,none') 

    # 2. Handle Date Logic
    default_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    default_end = datetime.now()

    if not t1:
        start_date = default_start
    else:
        try:
            start_date = datetime.strptime(t1, "%Y%m%d%H%M%S")
        except ValueError:
            return "Invalid date format for 'from'. Use YYYYMMDDHHMMSS", 400

    if not t2:
        end_date = default_end
    else:
        try:
            end_date = datetime.strptime(t2, "%Y%m%d%H%M%S")
        except ValueError:
            return "Invalid date format for 'to'. Use YYYYMMDDHHMMSS", 400
        
    # 3. Handle Filter Logic
    directions = [d.strip() for d in filter_param.split(',')]

    # 4. Query the Database
    conn = get_db()
    
    format_strings = ','.join(['%s'] * len(directions))
    
    sql_query = f"""
        SELECT id, direction, datetime, bruto_kg, neto_kg, produce, 
               containers, session_id, truck_id, truck_tara_kg
        FROM transactions
        WHERE datetime >= %s 
          AND datetime <= %s 
          AND direction IN ({format_strings})
    """

    params = [start_date, end_date] + directions

    results = []
    try:
        with conn.cursor() as cur:
            cur.execute(sql_query, params)
            rows = cur.fetchall()
            
            for row in rows:
                # FIX: Access by key names, not index numbers!
                
                containers_str = row['containers'] # Access by name
                containers_list = containers_str.split(',') if containers_str else []

                results.append({
                    "id": row['id'],
                    "direction": row['direction'],
                    "datetime": row['datetime'].strftime("%Y-%m-%d %H:%M:%S"),
                    "bruto_kg": row['bruto_kg'],
                    "neto_kg": row['neto_kg'],
                    "produce": row['produce'],
                    "containers": containers_list,
                    "session_id": row['session_id'],
                    "truck_id": row['truck_id'],
                    "truck_tara_kg": row['truck_tara_kg']
                })
                
    except Exception as e:
        print(f"Error fetching weight data: {e}")
        return jsonify({"error": "Database error"}), 500

    return jsonify(results), 200