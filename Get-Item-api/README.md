📦 Get Item API

This endpoint retrieves the weighing history and details for a specific item (Truck or Container).

📡 API Reference

GET /item/<id>

Returns the item's details, last known tara (weight), and a list of session IDs associated with it within a specific time range.

Path Parameters

Parameter

Type

Description

id

String

Required. The unique ID of the item (e.g., Truck License Plate 77-123-45 or Container ID CNT-101).

Query Parameters

Parameter

Type

Format

Default

Description

from

String

YYYYMMDDHHMMSS

1st of current month (00:00:00)

Start date/time for the history search.

to

String

YYYYMMDDHHMMSS

Now (Server Time)

End date/time for the history search.

🔄 Behavior & Defaults

Server Time: All time calculations assume the server's local time.

Unknown Item: If the <id> does not exist in the database, the API returns a 404 Not Found status code.

Tara Logic: Returns the last known tara weight for a truck. If unknown or not applicable, returns "na".

📝 Response Format

Returns a JSON object with the following structure:

{
  "id": <string>,
  "tara": <int> | "na",
  "sessions": [ <session_id_1>, <session_id_2>, ... ]
}


🧪 Example Requests

1. Basic Request (Using Defaults)

Fetches history from the 1st of this month until now.

Request:

GET /item/T-12345


Response (200 OK):

{
  "id": "T-12345",
  "tara": 5400,
  "sessions": ["1001", "1005", "1012"]
}


2. Custom Time Range

Fetches history for a specific range (e.g., Jan 1st, 2025 to Jan 2nd, 2025).

Request:

GET /item/C-999?from=20250101000000&to=20250102000000


Response (200 OK - Container example):

{
  "id": "C-999",
  "tara": "na",
  "sessions": ["2005", "2006"]
}


3. Item Not Found

Request:

GET /item/GHOST-TRUCK


Response (404 Not Found):

404 Not Found
