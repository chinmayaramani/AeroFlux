{{ config(
    materialized='incremental',
    unique_key='telemetry_id'
) }}

WITH telemetry AS (
    SELECT
        -- Creates a unique ID for every single snapshot row
        MD5(icao24 || '-' || time_position::text)            AS telemetry_id,
        icao24,
        MD5(icao24)                                          AS aircraft_key,
        
        -- Convert Unix epoch integers to native Postgres timestamps
        TO_TIMESTAMP(time_position)::TIMESTAMP WITHOUT TIME ZONE AS position_at,
        TO_TIMESTAMP(last_contact)::TIMESTAMP WITHOUT TIME ZONE  AS last_contact_at,
        
        longitude,
        latitude,
        baro_altitude,
        velocity,
        on_ground,
        CASE
            WHEN baro_altitude IS NULL OR on_ground = TRUE THEN 'Ground'
            WHEN baro_altitude < 3000                      THEN 'Low (<3k ft)'
            WHEN baro_altitude BETWEEN 3000 AND 25000      THEN 'Mid (3k–25k ft)'
            ELSE                                                'High (>25k ft)'
        END                                                  AS altitude_band
    FROM {{ ref('stg_live_flights') }}
)

SELECT * FROM telemetry
WHERE position_at IS NOT NULL

{% if is_incremental() %}
  -- Compares native timestamps smoothly to pull only new rows
  AND position_at > (SELECT MAX(position_at) FROM {{ this }})
{% endif %}