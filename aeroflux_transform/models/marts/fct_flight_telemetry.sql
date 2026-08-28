{{ config(materialized='table') }}

WITH staging AS (
    SELECT * FROM {{ ref('stg_live_flights') }}
)

SELECT
    MD5(CONCAT(icao24, '_', CAST(snapshot_time AS VARCHAR))) AS telemetry_id,
    icao24,
    snapshot_time,
    last_contact_time,
    longitude,
    latitude,
    baro_altitude,
    on_ground,
    velocity,
    true_track,
    vertical_rate,
    ingested_at
FROM staging