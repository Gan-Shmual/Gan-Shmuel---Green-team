from flask import Blueprint, Response,Flask
import traceback, pymysql, config

app = Flask(__name__)

def get_db():
    return pymysql.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )



@app.route("/health", methods=["GET"])
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
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)