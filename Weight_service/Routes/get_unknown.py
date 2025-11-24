from flask import Blueprint, request, jsonify
from db import get_db
from datetime import datetime

get_unknown_bp = Blueprint("get_unknown", __name__)

@get_unknown_bp.route("/unknown", methods=["GET"])
def get_unknown():

    conn = get_db()

    sql_unknown_weight = "SELECT weight FROM containers_registered WHERE weight IS NULL;"

    unknown_weights = []
    try:
        with conn.cursor() as cur:
            cur.execute(sql_unknown_weight)
            rows = cur.fetchall()
            
            for row in rows:
                unknown_weights.append({
                    "container_id": row['container_id'],
                    "weight": row['weight'],
                    "unit": row['unit']
                })
    except Exception as e:
        return f"Database query failed: {str(e)}", 500
    return jsonify(unknown_weights), 200

