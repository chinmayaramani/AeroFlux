{{ config(materialized='table') }}

WITH staging AS (
    SELECT * FROM {{ ref('stg_live_flights') }}
),

unique_aircraft AS (
    SELECT
        icao24,
        callsign,
        origin_country,
        MAX(snapshot_time) AS last_seen
    FROM staging
    GROUP BY icao24, callsign, origin_country
)

SELECT * FROM unique_aircraft