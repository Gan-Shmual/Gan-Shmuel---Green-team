import requests

weights_port = None

def from_weights(endpoint, data):
    response = requests.get(f'http://localhost:{weights_port}/{endpoint}', params=data)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def init_weights(app):
    global weights_port
    weights_port = app.config['WIGHT_PORT'] = app.config.get('WIGHT_PORT')
    try:
        status = from_weights('health', {})
        print(f'weights service is up: {status}')
    except Exception:
        print('Failed to connect to weights service.')