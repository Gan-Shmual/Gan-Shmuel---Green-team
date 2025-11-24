from flask import Blueprint, Response
from db import get_db
import traceback

get_health_bp = Blueprint("get_health", __name__)


@get_health_bp.route("/health", methods=["GET"])
def health():
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        return Response("OK", status=200)
    except Exception as e:
        # Print the full error stack trace to your terminal
        print("!!! DATABASE CONNECTION FAILED !!!")
        traceback.print_exc()
        return Response("Failure", status=500)