import requests
import pandas as pd
import psycopg2
from psycopg2 import extras

# 1. Connect to the OpenSky Live API (No API key required for public states data!)
def fetch_live_flights():
    print("Connecting to OpenSky Network API...")
    url = "https://opensky-network.org/api/states/all"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        states = data.get('states', [])
        
        # We only want a clean snapshot of the first 100 flights to keep things fast
        flight_list = []
        for s in states[:100]:
            flight_list.append({
                "icao24": s[0],
                "callsign": s[1].strip() if s[1] else "UNKNOWN",
                "origin_country": s[2],
                "time_position": s[3],
                "last_contact": s[4],
                "longitude": s[5],
                "latitude": s[6],
                "baro_altitude": s[7],
                "on_ground": s[8],
                "velocity": s[9]
            })
        
        df = pd.DataFrame(flight_list)
        print(f"Successfully fetched {len(df)} live flight records!")
        return df
    except Exception as e:
        print(f"Error fetching data from API: {e}")
        return None

# 2. Push the data into our local Docker PostgreSQL Database
def load_to_postgres(df):
    if df is None or df.empty:
        print("No data to load.")
        return

    print("Connecting to local PostgreSQL Warehouse...")
    conn = psycopg2.connect(
        host="postgres",
        database="aeroflux_warehouse",
        user="aviation_admin",
        password="aviation_password",
        port="5432"
    )
    cursor = conn.cursor()

    # Create a raw staging table if it doesn't exist yet
    create_table_query = """
    CREATE TABLE IF NOT EXISTS raw_flights (
        id SERIAL PRIMARY KEY,
        icao24 VARCHAR(50),
        callsign VARCHAR(50),
        origin_country VARCHAR(100),
        time_position INT,
        last_contact INT,
        longitude FLOAT,
        latitude FLOAT,
        baro_altitude FLOAT,
        on_ground BOOLEAN,
        velocity FLOAT,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (icao24, time_position)
    );
    """
    cursor.execute(create_table_query)
    conn.commit()

    # Fast bulk insert data into PostgreSQL
    columns = df.columns.tolist()
    values = [tuple(x) for x in df.to_numpy()]
    insert_query = f"INSERT INTO raw_flights ({','.join(columns)}) VALUES %s ON CONFLICT DO NOTHING"
    
    try:
        extras.execute_values(cursor, insert_query, values)
        conn.commit()
        print("Data successfully loaded into raw_flights table!")
    except Exception as e:
        print(f"Database insertion error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Run the ingestion process
    flight_data = fetch_live_flights()
    load_to_postgres(flight_data)