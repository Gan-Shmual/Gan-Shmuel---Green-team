❓ Unknown Containers API

This endpoint identifies containers that have been recorded in the system (e.g., during a truck transaction) but do not currently have a registered weight (Tara) in the database.

📡 API Reference

GET /unknown

Retrieves a list of all container IDs that have a NULL or missing weight value. This is useful for identifying which containers need to be registered via the /batch-weight endpoint.

Query Parameters

None.

📝 Response Format

Returns a JSON array of strings, where each string is the ID of a container with unknown weight.

[
  "container_id_1",
  "container_id_2",
  ...
]


If all containers have known weights, an empty array [] is returned.

🧪 Example Requests

1. Containers Found

Request:

GET /unknown


Response (200 OK):

[
  "CNT-777",
  "CNT-888",
  "X-900"
]


2. No Unknown Containers

Request:

GET /unknown


Response (200 OK):

[]
