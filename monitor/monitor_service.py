from flask  import Flask, jsonify, render_template
import requests
import time
import threading
from datetime import datetime
import pytz

app = Flask(__name__)

LOCAL_TZ = pytz.timezone('Asia/Jerusalem')

def get_local_time():
    return datetime.now(LOCAL_TZ)

#services to monitor
SERVICES = {
    "billing-service": {
        "url": "http://billing-service-prod:5001/health",
        "port": 8081
    },
    "weight-service": {
        "url": "http://weight-service-prod:5000/health",
        "port": 8082
    }
}

health_history = {
    "billing-service": [],
    "weight-service": []
}

current_status = {
    "billing-service": {"status": "unknown", "last_check": None, "response_time": None},
    "weight-service": {"status": "unknown", "last_check": None, "response_time": None}
}

MAX_HISTORY = 100

#check health of a single service
def check_service_health(service_name, service_config):
    try:
        start_time = time.monotonic()
        response = requests.get(service_config["url"], timeout=5)
        response_time = round((time.monotonic() - start_time) * 1000, 2)

        if response.status_code == 200:
            status = "healthy"
        else:
            status = "unhealthy"
    
    except requests.exceptions.Timeout:
        status = "timeout"
        response_time = None
    except requests.exceptions.ConnectionError:
        status = "down"
        response_time = None
    except Exception as e:
        status = "error"
        response_time = None
        print(f"Error checking {service_name}: {e}")
    
    current_status[service_name] = {
        "status": status,
        "last_check": get_local_time().strftime("%Y-%m-%d %H:%M:%S"),
        "response_time": response_time
    }

    health_history[service_name].append({
        "timestamp": get_local_time().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "response_time": response_time
    })

    if len(health_history[service_name]) > MAX_HISTORY:
        health_history[service_name] = health_history[service_name][-MAX_HISTORY:]
    
    return status

def check_all_services():
    results = {}
    for service_name, service_config in SERVICES.items():
        results[service_name] = check_service_health(service_name, service_config)
    return results

#checks health evrey 30 seconds
def background_health_check():
    while True:
        check_all_services()
        time.sleep(30)

#main dashboard page
@app.route("/")
def dashboard():
    return render_template("dashboard.html",
                            services=current_status,
                            last_updated=get_local_time().strftime("%Y-%m-%d %H:%M:%S"))

#monitor service health endpoint
@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "monitor"})

#current status of all services
@app.route("/api/status")
def api_status():
    return jsonify({
        "services": current_status,
        "timestamp": get_local_time().strftime("%Y-%m-%d %H:%M:%S")
    })

#get status of a specific service
@app.route("/api/status/<service_name>")
def api_service_status(service_name):
    if service_name not in current_status:
        return jsonify({"error": "Service not found"}), 404
    return jsonify({
        "service": service_name,
        "status": current_status[service_name],
        "timestamp": get_local_time().strftime("%Y-%m-%d %H:%M:%S")
    })

#get health history of a specific service
@app.route("/api/history/<service_name>")
def api_service_history(service_name):
    if service_name not in health_history:
        return jsonify({"error": "Service not found"}), 404
    return jsonify({
        "service": service_name,
        "history": health_history[service_name]
    })

#force health check
@app.route("/api/check")
def api_check_now():
    results = check_all_services()
    return jsonify({
        "results": results,
        "timestamp": get_local_time().strftime("%Y-%m-%d %H:%M:%S")
    })

#get summary of system health
@app.route("/api/summary")
def api_summary():
    healthy_count = sum(1 for s in current_status.values() if s["status"] == "healthy")
    total_count = len(current_status)

    if healthy_count == total_count:
        overall = "healthy"
    elif healthy_count == 0:
        overall = "down"
    else:
        overall = "degraded"
    
    return jsonify({
        "overall_status": overall,
        "healthy_services": healthy_count,
        "total_services": total_count,
        "services": current_status,
        "timestamp": get_local_time().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/api/rollback", methods=["POST"])
def rollback():
    try:
        import subprocess
        result = subprocess.run(
            ["/app/rollback.sh"],
            capture_output=True,
            text=True,
            timeout=300
        )

        success = (result.returncode == 0)
        status_code = 200 if success else 500

        return jsonify({
            "status": "success" if success else "failed",
            "output": result.stdout,
            "error": result.stderr
        }), status_code
    
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    health_thread = threading.Thread(target=background_health_check, daemon=True)
    health_thread.start()

    check_all_services()

    app.run(host="0.0.0.0", port=8085)