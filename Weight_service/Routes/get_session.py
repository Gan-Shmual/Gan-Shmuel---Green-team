from flask import Blueprint, jsonify, Response
from db import get_db

get_session_bp = Blueprint("session", __name__)

@get_session_bp.route("/session/<id>", methods=["GET"])
def get_session(id):
    conn = get_db()

    try:
        with conn.cursor() as cur:
            # Query matches REAL column names
            cur.execute("""
                SELECT 
                    id,
                    direction,
                    truck,
                    bruto,
                    truckTara,
                    neto
                FROM transactions
                WHERE id = %s
                LIMIT 1;
            """, (id,))

            row = cur.fetchone()

            # 1. Check if session exists
            if not row:
                return jsonify({"error": "Session not found"}), 404

            # 2. Build the base response (common to all directions)
            response = {
                "id": str(row['id']),
                "truck": row['truck'] if row['truck'] else "na",
                "bruto": row['bruto']
            }

            # 3. Add specific fields ONLY if direction is 'out'
            if row['direction'] == 'out':
                response["truckTara"] = row['truckTara']
                
                # Handle logic for neto: return "na" if it's null in DB, otherwise the int
                if row['neto'] is None:
                    response["neto"] = "na"
                else:
                    response["neto"] = row['neto']

            return jsonify(response), 200

    except Exception as e:
        print(f"Error: {e}") # Good for debugging logs
        return jsonify({"error": "Internal Server Error"}), 500
        
    finally:
        if conn:
            conn.close()
