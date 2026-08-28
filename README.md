# AeroFlux : Flight Telemetry ELT Pipeline
 
AeroFlux is a data engineering portfolio project that ingests real-time flight data, transforms it through a layered data model, and visualizes it in an interactive Power BI dashboard.
 
---
 
## What It Does
 
- **Ingest** — Python scripts scheduled by Apache Airflow pull live aircraft state vectors from the OpenSky Network API
- **Load** — Raw flight data is written directly into PostgreSQL (local) and Snowflake (cloud) data warehouses
- **Transform** — dbt cleans the raw data, models it into a star schema, and casts epoch timestamps to native SQL timestamps
- **Test & Document** — Automated schema assertions enforce data quality (`unique`, `not_null`) alongside auto-generated lineage DAG documentation
- **Visualize** — Power BI connects to the final tables and renders a map-based flight tracking dashboard with altitude and timeline filters
---
 
## Tech Stack
 
| Layer | Technology |
|---|---|
| **Orchestration** | Apache Airflow 2.7.1 |
| **Ingestion** | Python 3 |
| **Storage & Warehousing** | Snowflake (Cloud DW) / PostgreSQL 15 (Local DW) |
| **Transformation & Testing** | dbt Core (`dbt-snowflake`, `dbt-postgres`) |
| **Containerization** | Docker & Docker Compose |
| **Visualization** | Power BI Desktop |
 
---
 
## Getting Started
 
### Prerequisites
 
- **Docker Desktop** with WSL2 integration enabled (Windows)
- **Power BI Desktop**
- **Git**
### Step 1 — Clone and start the containers
 
```bash
git clone https://github.com/chinmayaramani/AeroFlux.git
cd AeroFlux
docker-compose up -d
```
 
> PostgreSQL will be available on port `5433` on your host machine.
 
### Step 2 — Run the dbt models & tests

```bash
cd aeroflux_transform

# Run against Snowflake Cloud Data Warehouse
dbt build --target dev_snowflake --profiles-dir .

# Run against Local PostgreSQL Database
dbt build --target dev --profiles-dir .

# View interactive documentation and lineage DAG
dbt docs generate --target dev_snowflake --profiles-dir .
dbt docs serve --profiles-dir .
```
 
### Step 3 — Open the dashboard
 
1. Open **`AeroFlux_Operations_Dashboard.pbix`** in Power BI Desktop
2. Go to **Home → Transform data → Data source settings**
3. Set the connection details:
```
Server   : localhost:5433
Database : aeroflux_warehouse
User     : aviation_admin
```
 
4. Click **Refresh** to load live data into the dashboard
> **Windows / WSL2 tip:** If `localhost:5433` times out, try `127.0.0.1:5433` instead. For a permanent fix, add `networkingMode=mirrored` to `C:\Users\<YourUser>\.wslconfig` and run `wsl --shutdown`.
 
---
 
## Data Model & Testing (dbt Core)
 
The dbt layer produces three star-schema models with 100% automated test coverage:
 
| Model | Type | Description | Key Tests |
|---|---|---|---|
| **`stg_live_flights`** | View | Cleaned and filtered staging layer | `not_null` (icao24, lat, lon) |
| **`dim_aircraft`** | Table | Dimension table containing unique aircraft records — icao24, callsign, country | `unique`, `not_null` (icao24) |
| **`fct_flight_telemetry`** | Table | Fact table recording positional snapshots — lat, lon, altitude, velocity | `unique`, `not_null` (telemetry_id) |
 
---
 
## Dashboard Preview
 
<img width="1307" height="731" alt="Screenshot 2026-06-17 192936" src="https://github.com/user-attachments/assets/aa74886f-c19f-4db7-9d1c-17f5940a9ec8" />

 
---
 
## Data Source
 
Flight state vector data is sourced from the [OpenSky Network](https://opensky-network.org/) REST API.
