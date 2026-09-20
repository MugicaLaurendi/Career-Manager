from pathlib import Path

import duckdb

# Connexion en mémoire
con = duckdb.connect('\data\database.duckdb')

# Etat initial
tables = con.execute("SHOW TABLES").fetchall()
print(f"INITIAL STATE : {tables}")


# ------------------ contracts_accepted -------------------


query = (f"""
    CREATE TABLE IF NOT EXISTS contracts_accepted (
        contract_category VARCHAR,
        departure_airport VARCHAR,
        arrival_airport VARCHAR,
        arrival_airport_category VARCHAR,
        distance_nm INTEGER,
        cargo VARCHAR,
        informations VARCHAR,
        latitude FLOAT,
        longitude FLOAT,
        altitude_ft FLOAT,
        country_code VARCHAR,
        city_name VARCHAR,
        departure_hour VARCHAR,
        departure_weather VARCHAR,
        reward INTEGER,
        user_id INTEGER
    );
""")
q = con.execute(query).fetchall()
print("contracts_accepted table created")


# ------------------ contracts_historical -------------------


query = (f"""
    CREATE TABLE IF NOT EXISTS contracts_historical (
        status VARCHAR,
        reward INTEGER,
        date DATE,
        contract_category VARCHAR,
        departure_airport VARCHAR,
        arrival_airport VARCHAR,
        arrival_airport_category VARCHAR,
        distance_nm INTEGER,
        cargo VARCHAR,
        informations VARCHAR,
        latitude FLOAT,
        longitude FLOAT,
        altitude_ft FLOAT,
        country_code VARCHAR,
        city_name VARCHAR,
        departure_hour VARCHAR,
        departure_weather VARCHAR,
        user_id INTEGER
        
    );
""")
q = con.execute(query).fetchall()
print("contracts_historical table created")


# ------------------ users_aircrafts -------------------


query = (f"""
    CREATE SEQUENCE users_aircrafts_id_seq;

    CREATE TABLE IF NOT EXISTS users_aircrafts (
        id INTEGER PRIMARY KEY DEFAULT nextval('users_aircrafts_id_seq'),
        user_id INTEGER,
        id_aircraft INTEGER,
        aircraft_model VARCHAR,
        hangar_location VARCHAR,
        fuel_level FLOAT,
        maintenance_level FLOAT,
        purchase_date DATE,
        manufacturer VARCHAR,
        category VARCHAR,
        engine_type VARCHAR,
        max_speed_kts INTEGER,
        cruise_speed_kts INTEGER,
        range_nm INTEGER,
        avg_fuel_consumption_gal_h FLOAT,
        service_ceiling_ft INTEGER,
        max_payload_kg INTEGER,
        max_passengers INTEGER,
        purchase_price INTEGER
    );
""")
q = con.execute(query).fetchall()
print("users_aircrafts table created")


# ------------------ users -------------------


query = (f"""
    CREATE SEQUENCE user_id_seq;
    
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY DEFAULT nextval('user_id_seq'),
        username VARCHAR,
        wallet INTEGER,
        current_aircraft INTEGER,
        current_location VARCHAR
    );
""")
q = con.execute(query).fetchall()
print("users table created")


# ------------------- INSERTIONS -------------------


query = (f"""
    INSERT INTO users (id, username, wallet, current_aircraft, current_location)
         VALUES (1, 'Edward Lawrence', 10000, 1, 'LFCH');
""")
try:
    q = con.execute(query).fetchall()
    print("User inserted")
except Exception:
    print("User already exists")
    pass
AIRCRAFT_CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "aircraft.csv"
STARTER_AIRCRAFT_ID = 20

query = (f"""
    INSERT INTO users_aircrafts (user_id, id_aircraft, aircraft_model, hangar_location, fuel_level, maintenance_level, purchase_date, manufacturer, category, engine_type, max_speed_kts, cruise_speed_kts, range_nm, avg_fuel_consumption_gal_h, service_ceiling_ft, max_payload_kg, max_passengers, purchase_price)
    SELECT 1, id, name, 'LFCH', 100, 100, DATE '2026-05-28', manufacturer, category, engine_type, max_speed_kts, cruise_speed_kts, range_nm, avg_fuel_consumption_gal_h, service_ceiling_ft, max_payload_kg, max_passengers, price_usd
    FROM read_csv_auto('{AIRCRAFT_CSV_PATH.as_posix()}')
    WHERE id = {STARTER_AIRCRAFT_ID};
""")
# try:
q = con.execute(query).fetchall()
print("User's aircraft inserted")
# except Exception:
#     print("User's aircraft already exists")
#     pass

# Etat final
tables = con.execute("SHOW TABLES").fetchall()
print(f"FINAL STATE : {tables}")