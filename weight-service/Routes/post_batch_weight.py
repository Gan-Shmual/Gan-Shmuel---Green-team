from flask import Blueprint, request, jsonify
from db import get_db
import os
import csv
import json
import traceback

post_batch_bp = Blueprint("post_batch_weight", __name__)

###############################################
# UNIT CONVERSION
###############################################
def convert_unit(value, unit):
    unit = str(unit).strip().lower()
    if unit == "kg":
        return int(value)
    if unit == "lbs":
        return int(round(float(value) * 0.453592))
    raise ValueError(f"Invalid unit '{unit}' (must be kg or lbs)")

###############################################
# DB HELPER: BATCH UPSERT
###############################################
def batch_upsert(data_list):
    """
    Receives a list of tuples: [(id, weight), (id, weight), ...]
    Performs a single connection open and bulk execution.
    """
    if not data_list:
        return 0, []

    conn = get_db()
    inserted_count = 0
    db_errors = []

    try:
        with conn.cursor() as cur:
            # We iterate and execute one by one to catch specific row errors,
            # BUT we use the same connection and commit only once at the end (or in chunks).
            # For maximum safety, we can commit after every execution, 
            # but since we reused the connection, it is much faster.
            
            sql = """
                INSERT INTO containers_registered (container_id, weight)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE
                    weight = VALUES(weight);
            """

            for container_id, weight in data_list:
                try:
                    cur.execute(sql, (container_id, weight))
                    inserted_count += 1
                except Exception as row_error:
                    db_errors.append(f"DB Error for {container_id}: {str(row_error)}")
        
        conn.commit() # Commit all changes at once
        
    except Exception as e:
        return 0, [f"Critical Database Error: {str(e)}"]

    return inserted_count, db_errors

###############################################
# PARSE CSV FILE
###############################################
def process_csv(filepath):
    valid_data = [] # Store valid rows here first [(id, weight), ...]
    errors = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)

        for row_idx, row in enumerate(reader):
            try:
                if not row or len(row) < 2:
                    continue

                # Skip header
                first = row[0].strip().lower()
                if first in ["id", "container_id", "truck", "container"]:
                    continue

                container_id = row[0].strip()
                raw_weight = row[1].strip()

                # --- Handle NULL weights ---
                if raw_weight.lower() in ["null", "", "none", "na"]:
                    valid_data.append((container_id, None))
                    continue

                # Valid weight
                weight_val = float(raw_weight)
                unit = row[2].strip().lower() if len(row) > 2 else "kg"
                weight_kg = convert_unit(weight_val, unit)

                valid_data.append((container_id, weight_kg))

            except Exception as e:
                errors.append(f"CSV row {row_idx + 1}: {str(e)}")

    # Write to DB in batch
    count, db_errors = batch_upsert(valid_data)
    errors.extend(db_errors)
    
    return count, errors

###############################################
# PARSE JSON FILE
###############################################
def process_json(filepath):
    valid_data = []
    errors = []

    with open(filepath, "r", encoding="utf-8") as f:
        items = json.load(f)

    if not isinstance(items, list):
        raise ValueError("JSON must contain a list of objects")

    for idx, obj in enumerate(items):
        try:
            # support both 'id' and 'container_id' keys
            container_id = obj.get("id") or obj.get("container_id")
            if not container_id:
                errors.append(f"JSON item {idx}: Missing 'id'")
                continue
                
            raw_weight = obj.get("weight", None)
            raw_unit = obj.get("unit", "kg")

            # --- NULL weight handling ---
            if raw_weight in [None, "null", "", "None", "NA"]:
                valid_data.append((container_id, None))
                continue

            # Normal case
            weight_val = float(raw_weight)
            weight_kg = convert_unit(weight_val, raw_unit)

            valid_data.append((container_id, weight_kg))

        except Exception as e:
            errors.append(f"JSON item {idx}: {str(e)}")

    # Write to DB in batch
    count, db_errors = batch_upsert(valid_data)
    errors.extend(db_errors)

    return count, errors

###############################################
# MAIN ENDPOINT
###############################################
@post_batch_bp.route('/batch-weight', methods=['POST'])
def post_batch_weight():
    filename = None
    filepath = None
    
    try:
        # 1. Check if a file is uploaded via Multipart/Form-Data (UI)
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
            
            filename = file.filename
            # Save file to /app/in/
            filepath = os.path.join('/app/in', filename)
            
            # Ensure directory exists
            os.makedirs('/app/in', exist_ok=True)
            file.save(filepath)

        # 2. Check if filename is provided in JSON/Form (API)
        else:
            data = request.get_json(silent=True) or request.form
            if data and "file" in data:
                filename = data["file"].strip()
                filepath = f"/app/in/{filename}"
            else:
                return jsonify({"error": "Missing required field: file (binary or filename string)"}), 400

        # 3. Validate File Existence and Format
        if not filename or not filepath:
            return jsonify({"error": "Could not determine file"}), 400

        ext = filename.lower().split(".")[-1]
        if ext not in ["csv", "json"]:
            return jsonify({"error": "Unsupported file format. Must be CSV or JSON"}), 400

        if not os.path.isfile(filepath):
            return jsonify({"error": f"File '{filename}' not found in /in"}), 404
        
        # 4. Process File
        processed = 0
        errors = []
        
        if ext == "csv":
            processed, errors = process_csv(filepath)
        elif ext == "json":
            processed, errors = process_json(filepath)

        return jsonify({
            "file": filename,
            "processed": processed,
            "errors": errors
        }), 200

    except Exception as e:
        print("!!! ERROR in /batch-weight !!!")
        traceback.print_exc()
        return jsonify({"error": f"Internal error: {str(e)}"}), 500