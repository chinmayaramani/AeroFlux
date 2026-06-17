# AeroFlux: Automated End-to-End Flight Telemetry Pipeline

AeroFlux is a data engineering pipeline designed to automate the ingestion, transformation, and visualization of real-time flight telemetry data. The system extracts data via automated ingestion scripts, loads it into a relational database, transforms raw metrics into analytical schemas, and exposes the processed data to a reporting dashboard.

## Technology Stack

The infrastructure is fully containerized and leverages the following technologies:
*   **Orchestration:** Apache Airflow manages and schedules the extraction pipelines.
*   **Transformation:** dbt (data build tool) handles database-level transformations, testing, and data modeling.
*   **Storage:** PostgreSQL serves as the centralized relational data warehouse.
*   **Containerization:** Docker and Docker Compose orchestrate the microservices to ensure environment consistency.
*   **Visualization:** Power BI Desktop serves as the business intelligence layer for operational tracking.

---

## System Workflow

The pipeline implements an ELT (Extract, Load, Transform) architecture operating in the following sequence:

1.  **Ingestion (Extract & Load):** Apache Airflow coordinates the execution of Python scripts that ingest real-time flight telemetry logs. The raw data is immediately written into staging tables within the PostgreSQL database.
2.  **Data Transformation (Transform):** dbt models execute modular SQL scripts inside the database. This layer cleans raw logs, applies schema constraints, and executes architectural optimizations. 
3.  **Upstream Optimization:** To improve reporting performance, the telemetry epoch time conversion was migrated upstream into the dbt transformation layer. Raw telemetry timestamps are cast directly into native PostgreSQL TIMESTAMP formats, eliminating calculation overhead at the reporting layer.
4.  **Reporting (Visualize):** Power BI establishes a direct connection to the finalized PostgreSQL database views, rendering pre-processed telemetry metrics with minimal query latency.

---

## Local Deployment and Access

Follow these instructions to deploy and explore the pipeline locally.

### Prerequisites
*   Docker and Docker Compose installed on the host machine.
*   Power BI Desktop (required to open and interact with the reporting file).

### Step 1: Initialize the Infrastructure
Clone the repository and spin up the containerized services in detached mode:
```bash
git clone [https://github.com/chinmayaramani/AeroFlux.git](https://github.com/chinmayaramani/AeroFlux.git)
cd AeroFlux
docker-compose up -d
