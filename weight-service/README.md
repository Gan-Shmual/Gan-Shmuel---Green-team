Weight Tracker Service API

This service manages the weighing of trucks and containers. It tracks sessions, handles tare weights (tara), and provides historical data for transactions.

<img width="1684" height="1105" alt="image" src="https://github.com/user-attachments/assets/ed467c0a-6da2-4c0e-8375-ae749a638666" />

Base URL

http://localhost:5000

Health Check

GET /health

Checks the system health and database connectivity.

Responses:

200 OK: Returns "OK". System is healthy.

500 Internal Server Error: Returns "Failure". Database connection failed or other critical resource is unavailable.

Weight Operations

POST /weight

Records a weight transaction. This is the main entry point for weighing trucks and containers.

Parameters (JSON or Form Data):

Parameter

Type

Description

direction

String

in, out, or none.

truck

String

License plate (e.g., "T-12345") or "na" if not applicable.

containers

String

Comma-delimited list of container IDs (e.g., "C-100,C-102").

weight

Integer

The total weight measured.

unit

String

kg or lbs. (Precision is ~5kg, decimals are ignored).

force

Boolean

true or false. Determines overwrite behavior (see Logic below).

produce

String

Type of produce (e.g., "orange") or "na".

Session Logic:

in: Generates a new session_id.

none: Generates a new session_id (used for standalone container weighing).

out: Finds the previous "in" session for this truck and uses that session_id.

Force Logic (force=true/false):

In -> In (Same Truck):

force=false: Returns Error (Truck already checked in).

force=true: Overwrites the previous "in" record.

Out -> Out (Same Truck):

force=false: Returns Error (Truck already checked out).

force=true: Overwrites the previous "out" record.

Out without In: Returns Error.

None after In: Returns Error.

Response (Success):

{
  "id": "1001", 
  "truck": "T-12345",
  "bruto": 5000,
  "truckTara": 2000,   // Only returned for direction='out'
  "neto": 3000         // Only returned for direction='out' ('na' if container weights unknown)
}


POST /batch-weight

Uploads a list of container tare weights from a file located in the /in folder. This is used to register a batch of new containers.

Parameters:

file: The filename to read from the /in folder (e.g., my_weights.json or data.csv).

Supported File Formats:

JSON: [{"id":"C-1", "weight":100, "unit":"kg"}, ...]

CSV: id,kg or id,lbs

Querying Data

GET /weight

Retrieves a list of weighing transactions based on time and direction filters.

Query Parameters:

from (t1): Start date (Format: YYYYMMDDHHMMSS). Default: Today at 00:00:00.

to (t2): End date (Format: YYYYMMDDHHMMSS). Default: Now.

filter (f): Comma-delimited list of directions (in,out,none). Default: in,out,none.

Response:

[
  {
    "id": 1001,
    "direction": "in",
    "bruto": 15000,
    "neto": "na",
    "produce": "orange",
    "containers": ["C-100", "C-101"]
  },
  ...
]


GET /item/<id>

Retrieves history for a specific Truck or Container.

Path Parameter:

id: The Truck License or Container ID.

Query Parameters:

from (t1): Start date. Default: 1st of current month at 00:00:00.

to (t2): End date. Default: Now.

Response:

Returns 404 if the ID does not exist.

Success:

{
  "id": "C-100",
  "tara": 500,       // For Truck: Last known tara. For Container: Registered weight.
  "sessions": ["1001", "1005", "1102"]
}


GET /session/<id>

Retrieves details for a specific weighing session.

Path Parameter:

id: The unique Session ID.

Response:

Returns 404 if the Session ID does not exist.

Success:

{
  "id": "1001",
  "truck": "T-12345",
  "bruto": 15000,
  "truckTara": 5000,   // Only if direction was 'out'
  "neto": 10000        // Only if direction was 'out'
}


GET /unknown

Returns a list of all containers that have been recorded in transactions but have no registered weight (tare) in the system.

Response:

["C-999", "C-888", "K-123"]
