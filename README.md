⚖️ Get Weight API

This microservice is responsible for querying the weight transaction history. It allows users to filter results by specific time ranges and truck directions.

📡 API Reference

GET /weight

Returns a list of weight transactions based on the provided filters.

Query Parameters

Parameter

Type

Format

Default

Description

t1

String

YYYYMMDDHHMMSS

Today 00:00

Start date/time for the search.

t2

String

YYYYMMDDHHMMSS

Now

End date/time for the search.

filter

String

CSV

in,out,none

Filter by direction. Accepts comma-separated list.

Example Requests

1. Get all transactions for today (Default):

GET http://localhost:5001/weight


2. Get transactions between 8:00 AM and 12:00 PM on Nov 21, 2025:

GET http://localhost:5001/weight?t1=20251121080000&t2=20251121120000


3. Get only "in" transactions:

GET http://localhost:5001/weight?filter=in


Response Format (JSON)

[
  {
    "id": 10,
    "direction": "in",
    "date": "2025-11-21 08:30:00",
    "bruto": 15000,
    "neto": 10000,
    "produce": "Oranges",
    "containers": ["CNT-101", "CNT-102"],
    "session_id": 1001,
    "truck": "77-123-45",
    "tara": 5000
  }
]


🛠️ Development

Running locally (without Docker):

Install dependencies: pip install -r requirements.txt

Set environment variables (MYSQL_HOST, MYSQL_USER, etc.)

Run: python app.py
