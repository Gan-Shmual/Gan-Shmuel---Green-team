from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

###############################################
# DATABASE CONNECTION
###############################################
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=3306
    )

###############################################
# VALIDATION UTILITIES
###############################################
def validate_required_fields(data):
    required = ["direction", "truck", "containers", "weight", "unit", "force", "produce"]
    return [f for f in required if f not in data]

def parse_force(force_raw): # dealing with force
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
def get_last_weigh(truck):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            id,
            direction,
            session_id,
            bruto_kg,
            datetime
        FROM transactions
        WHERE truck_id = %s
        ORDER BY datetime DESC
        LIMIT 1;
    """, (truck,))

    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def update_session_id(transaction_id, session_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE transactions SET session_id=%s WHERE id=%s;", (session_id, transaction_id))
    conn.commit()
    cur.close()
    conn.close()

###############################################
# DIRECTION RULE ENGINE
###############################################
def validate_direction_rules(direction, last_weigh, force):
    if last_weigh is None:
        return "OUT without a previous IN is not allowed" if direction == "out" else None

    last_dir = last_weigh["direction"] # get last dir

    if last_dir == "in" and direction == "none": # none after in gives error
        return "NONE after IN is not allowed"

    if direction == last_dir: # in after in, or out after out
        return None if force else f"{direction.upper()} after {direction.upper()} requires force=true"

    if direction == "out" and last_dir != "in": # out without in
        return "OUT without a previous IN is not allowed"

    return None

###############################################
# SESSION HANDLING
###############################################
def resolve_session_id(direction, last_weigh):
    if direction in ["in", "none"]: # new session
        return None
    return last_weigh["session_id"] if last_weigh else None # reuse previous session_id for OUT events

###############################################
# INSERT + UPDATE
###############################################
def save_transaction(direction, truck, containers, bruto, produce, session_id, last_weigh, force):
    conn = get_db_connection()
    cur = conn.cursor()

    if last_weigh and direction == last_weigh["direction"] and force:
        sql = """
            UPDATE transactions
            SET direction=%s, truck_id=%s, containers=%s, bruto_kg=%s, produce=%s, datetime=NOW()
            WHERE id=%s;
        """
        params = (direction, truck, ",".join(containers), bruto, produce, last_weigh["id"])
        cur.execute(sql, params)
        conn.commit()
        new_id = last_weigh["id"]
    else:
        sql = """
            INSERT INTO transactions
            (direction, truck_id, containers, bruto_kg, produce, session_id, datetime)
            VALUES (%s, %s, %s, %s, %s, %s, NOW());
        """
        params = (direction, truck, ",".join(containers), bruto, produce, session_id)
        cur.execute(sql, params)
        conn.commit()
        new_id = cur.lastrowid
        
        if direction in ["in", "none"]:
            update_session_id(new_id, new_id)
            session_id = new_id

    cur.close()
    conn.close()
    return new_id

###############################################
# OUT CALCULATIONS
###############################################
def calculate_out_values(transaction_id, session_id, containers, bruto_out):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # get IN bruto
    cur.execute("""
        SELECT bruto_kg FROM transactions
        WHERE session_id = %s AND direction='in'
        ORDER BY datetime DESC LIMIT 1;
    """, (session_id,))
    prev = cur.fetchone()
    truck_tara = prev["bruto_kg"] if prev else None

    # container taras
    unknown = False
    tara_sum = 0
    for cid in containers:
        cur.execute("SELECT weight_kg FROM containers WHERE id=%s", (cid,))
        row = cur.fetchone()
        if row is None:
            unknown = True
        else:
            tara_sum += row["weight_kg"]

    neto = None if unknown else bruto_out - truck_tara - tara_sum

    # update OUT row
    cur.execute("""
        UPDATE transactions SET truck_tara_kg=%s, neto_kg=%s WHERE id=%s;
    """, (truck_tara, neto, transaction_id))
    conn.commit()

    cur.close()
    conn.close()
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
@app.route('/weight', methods=['POST'])
def post_weight():
    data = request.get_json() or request.form

    # missing fields
    missing = validate_required_fields(data)
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # weight
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
    weight_kg = convert_to_kg(weight, unit)

    # last weigh
    last = get_last_weigh(truck)

    # rules
    error = validate_direction_rules(direction, last, force)
    if error:
        return jsonify({"error": error}), 400

    # session
    session_id = resolve_session_id(direction, last)

    # write to db
    tx_id = save_transaction(direction, truck, containers, weight_kg, produce, session_id, last, force)
    
    if direction in ["in", "none"]:
        session_id = tx_id

    # out values
    truck_tara = None
    neto = None
    if direction == "out":
        truck_tara, neto = calculate_out_values(tx_id, session_id, containers, weight_kg)

    # response
    return jsonify(build_response(direction, tx_id, truck, weight_kg, truck_tara, neto)), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
