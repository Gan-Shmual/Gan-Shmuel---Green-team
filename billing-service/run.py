from flaskr import create_app

app = create_app()

if __name__ == '__main__':
    port = app.config.get('APP_PORT')
    app.run(debug=True, host='0.0.0.0', port=port)