from flask import Blueprint, request, jsonify
from db import get_db
import traceback

post_weight_bp = Blueprint("post_weight", __name__)

###############################################
# VALIDATION UTILITIES (Unchanged)
###############################################
def validate_required_fields(data):
    required = ["direction", "truck", "containers", "weight", "unit", "force", "produce"]
    return [f for f in required if f not in data]

def parse_force(force_raw):
    if isinstance(force_raw, bool):
        return force_raw
    force_str = str(force_raw).strip().lower()
    if force_str in ["true", "1", "yes"]:
        return True
    if force_str in ["false", "0", "no"]:
        return False
    return None

def parse_containers(raw):
    if isinstance(raw, list):
        return raw
    return [c.strip() for c in raw.split(",") if c.strip()]

def normalize_input(data):
    direction = data["direction"].strip().lower()
    truck = data["truck"].strip()
    produce = data["produce"].strip().lower()
    unit = data["unit"].strip().lower()
    return direction, truck, produce, unit

###############################################
# WEIGHT UTILITIES (Unchanged)
###############################################
def convert_to_kg(weight, unit):
    return weight if unit == "kg" else int(round(weight * 0.453592))

###############################################
# DATABASE HELPERS
###############################################
def get_last_weigh(truck):
    conn = get_db()
    # We select specific columns to map them to a dictionary manually
    sql = """
        SELECT id, direction, session_id, bruto, datetime
        FROM transactions
        WHERE truck = %s
        ORDER BY datetime DESC
        LIMIT 1;
    """
    
    with conn.cursor() as cur:
        cur.execute(sql, (truck,))
        row = cur.fetchone()
        
        # Helper: Convert Tuple to Dict so the rest of your logic works
        # tuple index: 0=id, 1=direction, 2=session_id, 3=bruto, 4=datetime
        if row:
            return {
                "id": row[0],
                "direction": row[1],
                "session_id": row[2],
                "bruto": row[3],
                "datetime": row[4]
            }
    return None

def update_session_id(transaction_id, session_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("UPDATE transactions SET session_id=%s WHERE id=%s;", (session_id, transaction_id))
    conn.commit()

###############################################
# DIRECTION RULE ENGINE (Unchanged)
###############################################
def validate_direction_rules(direction, last_weigh, force):
    if last_weigh is None:
        return "OUT without a previous IN is not allowed" if direction == "out" else None

    last_dir = last_weigh["direction"]

    if last_dir == "in" and direction == "none":
        return "NONE after IN is not allowed"

    if direction == last_dir:
        return None if force else f"{direction.upper()} after {direction.upper()} requires force=true"

    if direction == "out" and last_dir != "in":
        return "OUT without a previous IN is not allowed"

    return None

###############################################
# SESSION HANDLING (Unchanged)
###############################################
def resolve_session_id(direction, last_weigh):
    if direction in ["in", "none"]:
        return None
    return last_weigh["session_id"] if last_weigh else None

###############################################
# INSERT + UPDATE
###############################################
def save_transaction(direction, truck, containers, bruto, produce, session_id, last_weigh, force):
    conn = get_db()
    new_id = None
    
    with conn.cursor() as cur:
        if last_weigh and direction == last_weigh["direction"] and force:
            sql = """
                UPDATE transactions
                SET direction=%s, truck=%s, containers=%s, bruto=%s, produce=%s, datetime=NOW()
                WHERE id=%s;
            """
            params = (direction, truck, ",".join(containers), bruto, produce, last_weigh["id"])
            cur.execute(sql, params)
            new_id = last_weigh["id"]
        else:
            sql = """
                INSERT INTO transactions
                (direction, truck, containers, bruto, produce, session_id, datetime)
                VALUES (%s, %s, %s, %s, %s, %s, NOW());
            """
            params = (direction, truck, ",".join(containers), bruto, produce, session_id)
            cur.execute(sql, params)
            new_id = cur.lastrowid
    
    conn.commit()

    if direction in ["in", "none"]:
        update_session_id(new_id, new_id)
        # Note: session_id update logic handled in wrapper, 
        # but we return new_id so the main function can update local var
    
    return new_id

###############################################
# OUT CALCULATIONS
###############################################
def calculate_out_values(transaction_id, session_id, containers, bruto_out):
    conn = get_db()
    truck_tara = None
    neto = None

    with conn.cursor() as cur:
        # 1. Get IN bruto (Truck Tara)
        cur.execute("""
            SELECT bruto FROM transactions
            WHERE session_id = %s AND direction='in'
            ORDER BY datetime DESC LIMIT 1;
        """, (session_id,))
        
        prev = cur.fetchone() # returns tuple (bruto,)
        truck_tara = prev[0] if prev else None

        # 2. Container Taras
        unknown = False
        tara_sum = 0
        
        # Loop through container IDs
        for cid in containers:
            cur.execute("SELECT weight FROM containers WHERE id=%s", (cid,))
            row = cur.fetchone() # returns tuple (weight,)
            if row is None:
                unknown = True
            else:
                tara_sum += row[0]

        neto = None if unknown or truck_tara is None else bruto_out - truck_tara - tara_sum

        # 3. Update OUT row
        cur.execute("""
            UPDATE transactions SET truckTara=%s, neto=%s WHERE id=%s;
        """, (truck_tara, neto, transaction_id))
    
    conn.commit()
    return truck_tara, neto

###############################################
# JSON RESPONSE BUILDER (Unchanged)
###############################################
def build_response(direction, transaction_id, truck, bruto, truck_tara, neto):
    resp = {
        "id": transaction_id,
        "truck": truck,
        "bruto": bruto
    }
    if direction == "out":
        resp["truckTara"] = truck_tara
        resp["neto"] = neto
    return resp

###############################################
# MAIN ENDPOINT
###############################################
@post_weight_bp.route('/weight', methods=['POST'])
def post_weight():
    # Helper to get data safely
    data = request.get_json() 
    if not data:
        data = request.form

    # missing fields
    missing = validate_required_fields(data)
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # weight validation
    try:
        weight = int(data["weight"])
        if weight <= 0:
            return jsonify({"error": "weight must be positive"}), 400
    except ValueError:
        return jsonify({"error": "weight must be integer"}), 400

    # normalize
    direction, truck, produce, unit = normalize_input(data)
    if direction not in ["in", "out", "none"]:
        return jsonify({"error": "invalid direction"}), 400
    if unit not in ["kg", "lbs"]:
        return jsonify({"error": "unit must be kg/lbs"}), 400

    # force
    force = parse_force(data["force"])
    if force is None:
        return jsonify({"error": "force must be true/false"}), 400

    containers = parse_containers(data["containers"])
    weight = convert_to_kg(weight, unit)

    try:
        # last weigh
        last = get_last_weigh(truck)

        # rules
        error = validate_direction_rules(direction, last, force)
        if error:
            return jsonify({"error": error}), 400

        # session
        session_id = resolve_session_id(direction, last)

        # write to db
        tx_id = save_transaction(direction, truck, containers, weight, produce, session_id, last, force)
        
        if direction in ["in", "none"]:
            session_id = tx_id

        # out values
        truck_tara = None
        neto = None
        if direction == "out":
            truck_tara, neto = calculate_out_values(tx_id, session_id, containers, weight)

        # response
        return jsonify(build_response(direction, tx_id, truck, weight, truck_tara, neto)), 200 # Changed to 201 for creation ideally, but keeping 200 per your code

    except Exception as e:
        print("!!! Error in POST /weight !!!")
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error"}), 500