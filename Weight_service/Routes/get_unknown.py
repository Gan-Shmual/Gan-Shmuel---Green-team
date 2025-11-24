from flask import Blueprint, jsonify
from db import get_db

get_unknown_bp = Blueprint('unknown_bp', __name__)

@get_unknown_bp.route('/unknown', methods=['GET'])
def get_unknown():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Logic: Find containers that exist in the containers table 
            # but have NULL or 0 weight. 
            # (Assuming your system adds containers to the DB when they are first seen)
            sql = "SELECT id FROM containers WHERE weight IS NULL OR weight = 0"
            cur.execute(sql)
            results = cur.fetchall()
            
            # Extract just the IDs into a list ['id1', 'id2']
            unknown_list = [row['id'] for row in results]
            
            return jsonify(unknown_list), 200

    except Exception as e:
        print(f"Error in get_unknown: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        if conn:
            conn.close()