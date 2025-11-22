from flask import Flask, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Denis: Mysql server variables for login
MYSQL_USER = os.environ.get("MYSQL_USER", "WeightGet")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "Pass")
MYSQL_DB = os.environ.get("MYSQL_DB", "weight")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "weight-db")


# Denis: Connetion to the database
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
)


#Denis: Disable the event system to save memory (not needed for this simple app).
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



#Denis: Initialize the ORM
db = SQLAlchemy(app)


# Rename class to Transactions to match the SQL table name in the slides
class Transactions(db.Model):
    __tablename__ = 'transactions' # Explicitly set table name

    id = db.Column(db.Integer, primary_key=True)
    
    datetime = db.Column(db.DateTime, default=datetime.now)
    
    direction = db.Column(db.String(10), nullable=False) # in/out/none
    
    truck_id = db.Column(db.String(50), nullable=False)
    
    containers = db.Column(db.String(10000)) # Comma separated list of containers
    
    bruto_kg = db.Column(db.Integer)
    
    truck_tara_kg = db.Column(db.Integer) # Needed for calculations
    
    neto_kg = db.Column(db.Integer)      # Net weight of fruit
    
    produce = db.Column(db.String(50))

    session_id = db.Column(db.Integer) # To link sessions


@app.route("/weight", methods=["GET"])
def get_weight():


    # 1. Get parameters from the URL (e.g., ?from=...&to=...&filter=...)
    # We use 'from' and 'to' as they are standard names, mapped to your t1/t2 idea
    t1 = request.args.get('t1')
    t2 = request.args.get('t2')
    filter_param = request.args.get('filter', 'in,out,none') # Default is all

    # 2. Handle Date Logic
    # Default: Start of today (00:00:00)
    default_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # Default: Now
    default_end = datetime.now()

    # Parse t1 (from)
    if not t1:
        start_date = default_start
    else:
        # Assuming format YYYYMMDDHHMMSS, e.g., "20250101000000"
        try:
            start_date = datetime.strptime(t1, "%Y%m%d%H%M%S")
        except ValueError:
            return "Invalid date format for 'from'. Use YYYYMMDDHHMMSS", 400

    # Parse t2 (to)
    if not t2:
        end_date = default_end
    else:
        try:
            end_date = datetime.strptime(t2, "%Y%m%d%H%M%S")
        except ValueError:
            return "Invalid date format for 'to'. Use YYYYMMDDHHMMSS", 400
        
        # 3. Handle Filter Logic
    # Split "in,out" into a list ['in', 'out'] and strip spaces
    directions = [d.strip() for d in filter_param.split(',')]

    # 4. Query the Database
    # We select rows where:
    # A. datetime is >= start_date
    # B. datetime is <= end_date
    # C. direction is INSIDE our list of allowed directions
    results = Transactions.query.filter(
        Transactions.datetime >= start_date,
        Transactions.datetime <= end_date,
        Transactions.direction.in_(directions)
    ).all()

    # 5. Format the response as JSON
    response_data = []
    for row in results:
        response_data.append({
        "id": row.id,
        "direction": row.direction,
        "date":row.datetime,
        # FIX: Use the new attribute names from the database
        "bruto": row.bruto_kg,   # <--- Changed from row.bruto
        "neto": row.neto_kg,     # <--- Changed from row.neto
        
        "produce": row.produce,
        "containers": row.containers.split(',') if row.containers else [],
        "session_id": row.session_id,

        # ADDED: The missing fields you mentioned
        "truck": row.truck_id,         # <--- Maps to truck_id column
        "tara": row.truck_tara_kg      # <--- Maps to truck_tara_kg column
    })
    
    return jsonify(response_data), 200


if __name__ == "__main__":
    #Eyal: Run the development server. In production use a WSGI server.
    app.run(debug=True, host='0.0.0.0', port=5000)