AeroFlux

Automated End-to-End Flight Telemetry Pipeline

AeroFlux is a data engineering portfolio project — a fully containerized ELT pipeline that ingests real-time aircraft state vectors from the OpenSky Network API, transforms raw telemetry through layered dbt models, and exposes a star-schema warehouse to an interactive Power BI dashboard.


Pipeline Architecture

OpenSky API  →  raw_flights  →  stg_live_flights  →  dim_aircraft
                                                  →  fct_flight_telemetry  →  Power BI
     ↑                ↑                ↑
  Python          PostgreSQL          dbt
  (Airflow)

Apache Airflow schedules Python ingestion scripts that pull live aircraft state vectors and land raw JSON/tuples into PostgreSQL. dbt models execute in layers — a staging view for cleansing, a dim_aircraft dimension for registry attributes, and a fct_flight_telemetry fact table for positional snapshots. Epoch timestamps are cast to native PostgreSQL TIMESTAMP inside dbt, so Power BI receives clean types with no Power Query conversion needed.


Technology Stack

LayerTechnologyOrchestrationApache Airflow 2.7.1Transformationdbt Core (postgres adapter)StoragePostgreSQL 15ContainerizationDocker & Docker ComposeVisualizationPower BI DesktopIngestion scriptsPython 3


dbt Model Layers

models/
├── staging/
│   └── stg_live_flights.sql        ← cleansing view (nullif, trim, coalesce)
└── marts/
    ├── dim_aircraft.sql             ← one row per unique icao24
    └── fct_flight_telemetry.sql     ← one row per positional snapshot

Key transformation decisions:


TO_TIMESTAMP(last_contact) and TO_TIMESTAMP(time_position) cast epoch integers to native TIMESTAMP WITHOUT TIME ZONE inside dbt — eliminating Power Query conversion overhead at the reporting layer.
dim_aircraft deduplicates by icao24 using ROW_NUMBER() ordered by last_contact DESC, keeping the most recently observed callsign and country per aircraft.
fct_flight_telemetry adds a derived altitude_band column (Ground / Low / Mid / High) so Power BI visuals can bucket altitudes without DAX SWITCH statements.
A surrogate key (MD5(icao24)) links the fact and dimension tables, replacing a brittle natural key join.



Local Deployment

Prerequisites


Docker Desktop with WSL2 integration enabled
Power BI Desktop (Windows host — required to open .pbix)
Git


Step 1 — Initialize infrastructure

Clone the repository and start all containers in detached mode. PostgreSQL binds on host port 5433 to avoid local port conflicts.

bashgit clone https://github.com/chinmayaramani/AeroFlux.git
cd AeroFlux
docker-compose up -d

Verify containers are healthy:

bashdocker ps
# aeroflux_postgres should show 0.0.0.0:5433->5432/tcp

Step 2 — Run dbt transformations

bashcd aeroflux_transform
dbt run

# Optionally validate with tests
dbt test

Step 3 — Connect Power BI


Open AeroFlux_Operations_Dashboard.pbix in Power BI Desktop.
Go to Home → Transform data → Data source settings.
Confirm the server is set to localhost:5433 and credentials match:


Server   : localhost:5433
Database : aeroflux_warehouse
User     : aviation_admin


Click Refresh on the canvas to load live data.



WSL2 networking note: If localhost:5433 times out from Windows tools (VS Code, Power BI), try 127.0.0.1:5433 first — this bypasses IPv6 resolution issues. For a permanent fix, add networkingMode=mirrored to C:\Users\<YourUser>\.wslconfig and restart WSL with wsl --shutdown.




Power BI Data Model

dim_aircraft [aircraft_key]  ──1──────*──  fct_flight_telemetry [aircraft_key]


Relationship direction: single (dimension filters fact, not vice versa)
Use position_at with Power BI's built-in date hierarchy for the flight timeline slicer
Set the slicer style to Between under Visualizations → Format → Slicer settings → Options → Style



Dashboard Preview

<img width="1307" height="731" alt="Screenshot 2026-06-17 192936" src="https://github.com/user-attachments/assets/707b07fd-1aff-4a8f-bab3-2854639250f1" />



Project Structure

AeroFlux/
├── dags/                            # Airflow DAG definitions
├── aeroflux_transform/              # dbt project
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_live_flights.sql
│   │   └── marts/
│   │       ├── dim_aircraft.sql
│   │       └── fct_flight_telemetry.sql
│   ├── dbt_project.yml
│   └── profiles.yml
├── ingestion/                       # Python extraction scripts
├── AeroFlux_Operations_Dashboard.pbix
├── docker-compose.yml
└── README.md


Acknowledgements


Flight state vector data sourced from the OpenSky Network REST API.
