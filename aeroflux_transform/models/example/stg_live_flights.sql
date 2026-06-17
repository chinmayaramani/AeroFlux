{{ config(materialized='table') }}

WITH source_data AS (
    SELECT 
        icao24,
        callsign,
        COALESCE(NULLIF(origin_country, ''), 'Unknown') AS origin_country,
        time_position,
        last_contact,
        longitude,
        latitude,
        baro_altitude,
        on_ground,
        velocity
    FROM {{ source('public', 'raw_flights') }}
)

SELECT * FROM source_data
WHERE icao24 IS NOT NULL