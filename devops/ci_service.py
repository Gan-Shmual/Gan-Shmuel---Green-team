from flask import Flask, request, jsonify
import subprocess
import hmac
import hashlib
import os

app = Flask(__name__)

WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "").encode()

def verify_signature(payload_body, signature_header):
    if not WEBHOOK_SECRET:
        print("Warning: No webhook secret configured")
    
    if not signature_header:
        return False
    
    hash_object = hmac.new(WEBHOOK_SECRET, msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)

@app.get("/health")
def health():
    return "OK",200

@app.post("/webhook")
def webhook():
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_signature(request.get_data(), signature):
        return jsonify({"error: Invalid signature"}), 403
    
    event = request.headers.get("X-GitHub-Event")
    print(f"[CI] Recevied event: {event}")

    if event != "push":
        return jsonify({"status": "ignored", "reason": f"Event type: {event}"}, 200)
    
    payload = request.get_json()

    ref = payload.get("ref", "")
    branch = ref.replace("refs/heads/", "")
    print(f"[CI] Push to branch: {branch}")

    if branch != "development":
        return jsonify({"status": "ignored", "reason": f"Branch: {branch}"}), 200
    
    print(f"[CI] Triggering pipline for branch: {branch}")
    try:
        subprocess.check_call(["./ci_pipeline.sh"])
        return jsonify({"status": "Success"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"status" : "Failed", "Error": str(e)}), 500
    

@app.post("/trigger")
def trigger():
    payload = request.get_json()
    try:
        subprocess.check_call(["./ci_pipline.sh"])
        return jsonify({"status: Success"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "Failed", "Error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 8000)