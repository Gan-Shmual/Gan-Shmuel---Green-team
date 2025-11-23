from flask import Blueprint, send_file, request, jsonify
from flaskr.db import db
import pandas as pd
from flaskr.models.biling import Rate
import os
from sqlalchemy import delete

IN_FOLDER = "/app/data/init/in"
LATEST = os.path.join(IN_FOLDER, "latest_rates.xlsx")

rates = Blueprint('rates', __name__)

@rates.post('/rates')
def upload_rates():
    data = request.get_json()
    filename = data.get("filename")
    path = os.path.join(IN_FOLDER, filename)

    if not os.path.exists(path):
        return jsonify({"error": f"File '{filename}' not found in /in"}), 404

    df = pd.read_excel(path)
    # drop if there are NA in product id or rate; fill with All if provider is missing 
    df['MyColumn'].fillna('ALL', inplace=True)
    df = df.dropna(how='any')
    

    # convert to list-of-dicts suitable for bulk insert
    mappings = df.to_dict(orient='records')

    try:
        db.session.execute(delete(Rate))
        # bulk insert 
        if mappings:
            db.session.bulk_insert_mappings(Rate, mappings)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    #save the rates as rates_latest
    df.to_excel(LATEST, index=False)
    
    return jsonify({"message": f"Loaded {filename}", "stored_as": "latest_rates.xlsx"}), 200


@rates.get('/rates')
def download_rates():
    if not os.path.exists(LATEST):
        return jsonify({"error": "No rates uploaded yet"}), 404

    return send_file(
        LATEST,
        as_attachment=True,
        download_name="rates.xlsx"
    )
