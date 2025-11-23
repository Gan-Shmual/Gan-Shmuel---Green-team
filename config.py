import os

DB_HOST = os.getenv("DB_HOST", "weight-db")
DB_USER = os.getenv("DB_USER", "weight_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "weight_pass")
DB_NAME = os.getenv("DB_NAME", "weight")

