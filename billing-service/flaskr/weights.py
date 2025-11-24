import requests

weights_port = None
weights_host = None

def from_weights(endpoint, data):
    response = requests.get(f'http://{weights_host}:{weights_port}/{endpoint}', params=data)
    if response.status_code == 200:
        return response
    else:
        response.raise_for_status()

def init_weights(app):
    global weights_port, weights_host
    weights_host = app.config.get('WEIGHTS_HOST')
    weights_port = app.config.get('WEIGHTS_PORT')
    try:
        status = from_weights('health', {})
        print(f'weights service is up: {status}')
    except Exception:
        print(f'Failed to connect to weights service. http://{weights_host}:{weights_port}/health')