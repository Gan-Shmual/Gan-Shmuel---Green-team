from flask import Blueprint, request, jsonify
from db import get_db
import traceback

post_weight_bp = Blueprint("post_weight", __name__)

###############################################
# VALIDATION UTILITIES
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
# WEIGHT UTILITIES
###############################################
def convert_to_kg(weight, unit):
    return weight if unit == "kg" else int(round(weight * 0.453592))

###############################################
# DATABASE HELPERS
###############################################
# Fetch last weigh for a truck (from transactions)
def get_last_weigh(truck):
    conn = get_db()
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
        # If found, return as dict
        if row:
            return {
                "id": row["id"],
                "direction": row["direction"],
                "session_id": row["session_id"],
                "bruto": row["bruto"],
                "datetime": row["datetime"]
            }

    return None
# Update session_id for a transaction 
def update_session_id(transaction_id, session_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("UPDATE transactions SET session_id=%s WHERE id=%s;", (session_id, transaction_id))
    conn.commit()

def validate_truck_exists(truck_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT container_id 
            FROM containers_registered 
            WHERE container_id = %s
        """, (truck_id,))
        row = cur.fetchone()
        return row is not None

###############################################
# DIRECTION RULE ENGINE
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
# SESSION HANDLING
###############################################
# used for out 
# it attaches the transaction to the previous in session 
def resolve_session_id(direction, last_weigh):
    if direction in ["in", "none"]:
        return None
    return last_weigh["session_id"] if last_weigh else None

###############################################
# Tara & Containers fetch
###############################################
def get_truck_tara(truck_id):
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT weight 
                FROM containers_registered 
                WHERE container_id = %s
            """, (truck_id,))
            result = cur.fetchone()
            
            if result and result['weight'] is not None:
                return result['weight']
            
            # If not found in db, check previous transactions
            cur.execute("""
                SELECT truckTara 
                FROM transactions 
                WHERE truck = %s AND truckTara IS NOT NULL
                ORDER BY datetime DESC 
                LIMIT 1
            """, (truck_id,))
            result = cur.fetchone()
            return result['truckTara'] if result else None
            
    except Exception as e:
        print(f"Error fetching tara for truck {truck_id}: {e}")
        return None
    
def get_container_info(container_id):
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT container_id, weight 
                FROM containers_registered 
                WHERE container_id = %s
            """, (container_id,))
            return cur.fetchone()
    except Exception as e:
        print(f"Error fetching container {container_id}: {e}")
        return None

def get_all_containers_info(containers):
    containers_data = []
    for container_id in containers:
        container_info = get_container_info(container_id.strip())
        if container_info:
            containers_data.append(container_info)
    return containers_data

def validate_containers(containers):
    conn = get_db()
    errors = []

    with conn.cursor() as cur:
        for cid in containers:
            cid = cid.strip()

            cur.execute("""
                SELECT weight 
                FROM containers_registered 
                WHERE container_id = %s
            """, (cid,))
            row = cur.fetchone()

            if row is None:
                errors.append(f"{cid} not registered, please register it first")
            elif row["weight"] is None:
                errors.append(f"{cid} NULL weight in database, please update its weight first")

    return errors

###############################################
# INSERT + UPDATE
###############################################
def save_transaction(direction, truck, containers, bruto, produce, session_id, last_weigh, force):
    conn = get_db()
    new_id = None
    
    # Fetch truck tara from database
    truck_tara = get_truck_tara(truck)
    if truck_tara is None:
        print(f"Warning: Could not fetch truckTara for truck {truck}")
        truck_tara = None  # Store as NULL in database
    
    # Fetch container information (if needed)
    containers_info = get_all_containers_info(containers)
    print(f"Fetched info for {len(containers_info)} containers")
    
    with conn.cursor() as cur:
        if last_weigh and direction == last_weigh["direction"] and force:
            sql = """
                UPDATE transactions
                SET direction=%s, truck=%s, containers=%s, bruto=%s, truckTara=%s, produce=%s, datetime=NOW()
                WHERE id=%s;
            """
            params = (direction, truck, ",".join(containers), bruto, truck_tara, produce, last_weigh["id"])
            cur.execute(sql, params)
            new_id = last_weigh["id"]
        else:
            sql = """
                INSERT INTO transactions
                (direction, truck, containers, bruto, truckTara, produce, session_id, datetime)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW());
            """
            params = (direction, truck, ",".join(containers), bruto, truck_tara, produce, session_id)
            cur.execute(sql, params)
            new_id = cur.lastrowid
    
    conn.commit()

    if direction in ["in", "none"]:
        update_session_id(new_id, new_id)
    
    return new_id

###############################################
# OUT CALCULATIONS
###############################################
def calculate_out_values(transaction_id, session_id, containers, bruto_out, truck):
    conn = get_db()
    truck_tara = None
    neto = None

    with conn.cursor() as cur:
        # Container Taras
        unknown = False
        tara_sum = 0
        
        for cid in containers:
            cur.execute("SELECT weight FROM containers_registered WHERE container_id=%s", (cid,))
            row = cur.fetchone()  # dict: {"weight": int}

            if row is None or row["weight"] is None:  # Check for NULL weight
                unknown = True
            else:
                tara_sum += row["weight"]

        truck_tara = get_truck_tara(truck)
        if truck_tara is None:
            print(f"Warning: Could not fetch truckTara for truck {truck}")
            truck_tara = None  # Store as NULL in database
        
        # Calculate neto
        if unknown or truck_tara is None:
            neto = None
        else:
            neto = bruto_out - truck_tara - tara_sum

        # Update OUT transaction
        cur.execute("""
            UPDATE transactions SET truckTara=%s, neto=%s
            WHERE id=%s;
        """, (truck_tara, neto, transaction_id))
    
    conn.commit()
    return truck_tara, neto


###############################################
# JSON RESPONSE BUILDER
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

    # Validate truck existence
    if truck.lower() not in ["na", "none"]:
        if not validate_truck_exists(truck):
            return jsonify({
                "error": "Truck is not registered. Please register your truck and come back (use batch weight)."
            }), 400

    # Validate containers - check for unknown or NULL weight containers
    unknown_containers = validate_containers(containers)
    if unknown_containers:
        return jsonify({
            "error": f"Unknown containers: {', '.join(unknown_containers)}"
        }), 400

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
            truck_tara, neto = calculate_out_values(tx_id, session_id, containers, weight, truck)

        # response
        return jsonify(build_response(direction, tx_id, truck, weight, truck_tara, neto)), 200

    except Exception as e:
        print("!!! Error in POST /weight !!!")
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error"}), 500