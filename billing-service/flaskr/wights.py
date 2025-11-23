import requests

wights_port = None

def from_wights(endpoint, data):
    response = requests.get(f'http://localhost:{wights_port}/{endpoint}', params=data)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def init_wights(app):
    global wights_port
    wights_port = app.config['WIGHT_PORT'] = app.config.get('WIGHT_PORT')
    try:
        status = from_wights('health', {})
        print(f'Wights service is up: {status}')
    except Exception:
        print('Failed to connect to Wights service, using dammy data.')