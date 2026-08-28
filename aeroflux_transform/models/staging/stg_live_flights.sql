WITH source AS (
    SELECT * FROM {{ source('raw_data', 'raw_flights') }}
),

renamed AS (
    SELECT
        TRIM(icao24) AS icao24,
        TRIM(callsign) AS callsign,
        TRIM(origin_country) AS origin_country,
        {% if target.type == 'snowflake' %}
            TO_TIMESTAMP_NTZ(time_position) AS snapshot_time,
            TO_TIMESTAMP_NTZ(last_contact) AS last_contact_time,
        {% else %}
            TO_TIMESTAMP(time_position) AS snapshot_time,
            TO_TIMESTAMP(last_contact) AS last_contact_time,
        {% endif %}
        longitude,
        latitude,
        baro_altitude,
        on_ground,
        velocity,
        true_track,
        vertical_rate,
        ingested_at
    FROM source
    WHERE icao24 IS NOT NULL
      AND latitude IS NOT NULL
      AND longitude IS NOT NULL
)

SELECT * FROM renamed