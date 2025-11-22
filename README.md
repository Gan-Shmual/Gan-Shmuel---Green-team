🩺 Health API

This microservice monitors the connectivity and status of the Gan Shmuel Weight System. It is primarily used to verify that the database is reachable and the system is operational.

📡 API Reference

GET /health

Performs a connectivity check to the MySQL database and returns the system status.

Response Codes

200 OK: Database is connected and system is healthy.

500 Internal Server Error: Database connectivity failed.

Response Example

{
  "status": "OK",
  "database": "Connected",
  "timestamp": "2025-11-21 10:00:00"
}


⚙️ Configuration

The service relies on the following environment variables (automatically provided by docker-compose.yml):

DB_HOST: Hostname of the MySQL container (default: weight-db)

DB_USER: Database username

DB_PASSWORD: Database password

DB_NAME: Database name
