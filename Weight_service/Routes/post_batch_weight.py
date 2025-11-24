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
# UPDATE/INSERT CONTAINER WEIGHT
###############################################
def upsert_container(container_id, weight, unit):
    conn = get_db()
    with conn.cursor() as cur:
        sql = """
            INSERT INTO containers_registered (container_id, weight, unit)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                weight = VALUES(weight),
                unit = VALUES(unit);
        """
        cur.execute(sql, (container_id, weight, unit))
    conn.commit()

###############################################
# PARSE CSV FILE
###############################################
def process_csv(filepath):
    processed = 0
    errors = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)

        for row in reader:
            try:
                if not row or len(row) < 2:
                    continue

                # Skip header
                first = row[0].strip().lower()
                if first in ["id", "container_id"]:
                    continue

                container_id = row[0].strip()
                raw_weight = row[1].strip()

                # --- Handle NULL weights ---
                if raw_weight.lower() in ["null", "", "none", "na"]:
                    upsert_container(container_id, None, None)
                    processed += 1
                    errors.append(f"CSV row {row}: weight is NULL, inserted as NULL")
                    continue

                # Valid weight
                weight_val = float(raw_weight)
                unit = row[2].strip().lower() if len(row) > 2 else "kg"
                weight_kg = convert_unit(weight_val, unit)

                upsert_container(container_id, weight_kg, "kg")
                processed += 1

            except Exception as e:
                errors.append(f"CSV row {row}: {str(e)}")

    return processed, errors

###############################################
# PARSE JSON FILE
###############################################
def process_json(filepath):
    processed = 0
    errors = []

    with open(filepath, "r", encoding="utf-8") as f:
        items = json.load(f)

    if not isinstance(items, list):
        raise ValueError("JSON must contain a list of objects")

    for obj in items:
        try:
            container_id = obj["id"]
            raw_weight = obj.get("weight", None)
            raw_unit = obj.get("unit", None)

            # --- NULL weight handling ---
            if raw_weight in [None, "null", "", "None", "NA"]:
                upsert_container(container_id, None, None)
                processed += 1
                errors.append(f"JSON object {obj}: weight is NULL, inserted as NULL")
                continue

            # Normal case
            weight_val = float(raw_weight)
            unit = raw_unit.lower() if raw_unit else "kg"
            weight_kg = convert_unit(weight_val, unit)

            upsert_container(container_id, weight_kg, "kg")
            processed += 1

        except Exception as e:
            errors.append(f"JSON object {obj}: {str(e)}")

    return processed, errors

###############################################
# MAIN ENDPOINT
###############################################
@post_batch_bp.route('/batch-weight', methods=['POST'])
def post_batch_weight():
    data = request.get_json() or request.form

    if "file" not in data:
        return jsonify({"error": "Missing required field: file"}), 400

    filename = data["file"].strip()
    filepath = f"/app/in/{filename}"

    ext = filename.lower().split(".")[-1]
    # check extnesion
    if ext not in ["csv", "json"]:
        return jsonify({"error": "Unsupported file format. Must be CSV or JSON"}), 400

    if not os.path.isfile(filepath):
        return jsonify({"error": f"File '{filename}' not found in /in"}), 404
    
    try:
        if ext == "csv":
            processed, errors = process_csv(filepath)

        elif ext == "json":
            processed, errors = process_json(filepath)

        else:
            return jsonify({"error": "Unsupported file format. Must be CSV or JSON"}), 400

    except Exception as e:
        print("!!! ERROR in /batch-weight !!!")
        traceback.print_exc()
        return jsonify({"error": f"Internal error while processing file: {str(e)}"}), 500

    return jsonify({
        "file": filename,
        "processed": processed,
        "errors": errors
    }), 200
