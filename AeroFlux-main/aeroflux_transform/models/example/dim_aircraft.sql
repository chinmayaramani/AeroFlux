{{ config(materialized='table') }}

WITH ranked AS (
    SELECT
        icao24,
        callsign,
        origin_country,
        last_contact,
        CASE WHEN origin_country = 'Unknown' THEN TRUE ELSE FALSE END AS is_origin_unknown,
        ROW_NUMBER() OVER (PARTITION BY icao24 ORDER BY last_contact DESC) AS rn
    FROM {{ ref('stg_live_flights') }}
)

SELECT
    MD5(icao24)          AS aircraft_key,
    icao24,
    callsign,
    origin_country,
    is_origin_unknown
FROM ranked
WHERE rn = 1