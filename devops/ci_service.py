from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.get("/health")
def health():
    return "OK",200

@app.post("/trigger")
def trigger():
    payload = request.get_json()
    #payload inspection will be done here later


    #for now
    try:
        subprocess.check_call(["/app/devops/ci_pipeline.sh"])
        return jsonify({"status": "Success"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"status" : "Failed", "Error": str(e)}),500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8000)