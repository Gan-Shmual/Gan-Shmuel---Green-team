from os import environ

DB_HOST = environ.get('DB_HOST', 'db')
DB_USER = environ.get('DB_USER', 'root')
DB_NAME = environ.get('DB_NAME', 'billdb')
DB_PASSWORD = environ.get('DB_PASSWORD', 'pss11')
DB_PORT = int(environ.get('DB_PORT', 3306))
APP_PORT = int(environ.get('APP_PORT', 5000))