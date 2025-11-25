from flask import Blueprint, jsonify, request
from datetime import datetime
from db import get_db

get_item_bp = Blueprint("get_item", __name__)

@get_item_bp.route("/item/<id>", methods=["GET"])
def get_item(id):
    # 1. Get Date parameters
    t1 = request.args.get('t1')
    t2 = request.args.get('t2')

    # 2. Handle Date Logic
    # Req: default t1 is "1st of month at 000000"
    now = datetime.now()
    default_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    default_end = now

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

    # 3. Query the Database
    conn = get_db()
    
    # We need to determine if 'id' is a Truck or a Container to get the Tara
    # And we need to get the list of sessions.
    
    tara_value = "na"
    item_found = False

    try:
        with conn.cursor() as cur:
            # --- STEP A: Check if it's a REGISTERED CONTAINER ---
            # Containers have their own table
            sql_container = "SELECT weight FROM containers_registered WHERE container_id = %s"
            cur.execute(sql_container, (id,))
            container_row = cur.fetchone()

            if container_row:
                item_found = True
                tara_value = container_row['weight'] # Using DictCursor keys
            else:
                # --- STEP B: Check if it's a TRUCK ---
                # Trucks live in transactions. We want the LAST known tara.
                sql_truck = """
                    SELECT truckTara 
                    FROM transactions 
                    WHERE truck = %s 
                    ORDER BY datetime DESC 
                    LIMIT 1
                """
                cur.execute(sql_truck, (id,))
                truck_row = cur.fetchone()
                
                if truck_row:
                    item_found = True
                    tara_value = truck_row['truckTara']

            # If we didn't find it in containers OR transactions, return 404
            if not item_found:
                return jsonify({"error": "Item not found"}), 404

            # --- STEP C: Get Sessions ---
            # We need sessions where this ID was involved (either as truck OR container)
            # between the dates.
            # Note: The 'containers' column is a string (e.g., "C1,C2"). 
            # We use LIKE for simple matching or exact match if it's just one.
            
            sql_sessions = """
                SELECT DISTINCT session_id 
                FROM transactions 
                WHERE (truck = %s OR containers LIKE %s)
                  AND datetime >= %s 
                  AND datetime <= %s
            """
            
            # We add % around the ID for the container search 
            # (matches "C1" inside "C1,C2" or "C5,C1")
            container_search = f"%{id}%" 
            
            cur.execute(sql_sessions, (id, container_search, start_date, end_date))
            session_rows = cur.fetchall()
            
            # Extract just the session IDs into a list
            sessions_list = [str(row['session_id']) for row in session_rows]

            # 4. Return JSON
            response = {
                "id": id,
                "tara": tara_value,
                "sessions": sessions_list
            }
            return jsonify(response), 200

    except Exception as e:
        print(f"Error fetching item data: {e}")
        return jsonify({"error": "Database error"}), 500