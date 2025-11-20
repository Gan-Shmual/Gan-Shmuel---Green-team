# 🚛 Gan Shmuel Weight System

The **Weight System** is the core component of the Gan Shmuel factory architecture. It tracks the entry and exit of trucks, manages container weights, and calculates the net weight of produce for billing purposes.

## 🚀 Getting Started

This service is containerized using Docker.

### Prerequisites
* Docker
* Docker Compose

### Installation & Running
1.  Navigate to the project root.
2.  Build and start the services:
    ```bash
    docker-compose up --build -d
    ```
3.  The service will be available at `http://localhost:<PORT>` (Check your `docker-compose.yml` for the exposed port).

## 🏗️ Architecture

* [cite_start]**Language:** Python (Flask) [cite: 94]
* [cite_start]**Database:** MySQL (Weight DB) [cite: 101]
* [cite_start]**Deployment:** Docker Containers [cite: 95]

The system calculates the net weight using the formula:
$$Net = Gross - (TruckTara + \sum ContainerTara)$$

## 🔌 API Documentation

### Health Check
* **GET** `/health`
    * [cite_start]Checks if the server and database connection are active[cite: 57].

### Weighing Operations
* **POST** `/weight`
    * **Description:** Main entry point for weighing trucks. [cite_start]Handles both inbound (Gross) and outbound (Tara) weighing sessions[cite: 51].
    * **Body:** JSON object containing truck license and direction.

* **POST** `/batch-weight`
    * [cite_start]**Description:** Upload a CSV or JSON file containing container IDs and their unit weights[cite: 46, 52].
    * **Usage:** Used to populate the `Containers_registered` database.

### Reports & Data Retrieval
* **GET** `/weight`
    * [cite_start]**Description:** Returns a list of weighing records, filtered by time (from/to) and filter (in/out/none)[cite: 54].

* **GET** `/item/<id>`
    * [cite_start]**Description:** Returns history for a specific Truck ID or Container ID[cite: 55].

* **GET** `/session/<id>`
    * [cite_start]**Description:** Returns details of a specific weighing session[cite: 56].

* **GET** `/unknown`
    * [cite_start]**Description:** Returns a list of containers spotted during weighing that are not yet registered in the system[cite: 53].

## 🧪 Testing

To run the End-to-End (E2E) tests:
```bash
# Command to run your tests (e.g., python -m pytest)
