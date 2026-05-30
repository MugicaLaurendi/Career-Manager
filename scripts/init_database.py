import duckdb

# Connexion en mémoire
con = duckdb.connect('\data\database.duckdb')

# Etat initial
tables = con.execute("SHOW TABLES").fetchall()
print("INITIAL STATE :")
print(tables)

query = (f"""
    CREATE TABLE IF NOT EXISTS contracts_accepted (
        contract_category VARCHAR,
        destination VARCHAR,
        destination_category VARCHAR,
        distance_nm INTEGER,
        cargo VARCHAR,
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

query = (f"""
    CREATE TABLE IF NOT EXISTS contracts_historical (
        contract_category VARCHAR,
        destination VARCHAR,
        destination_category VARCHAR,
        distance_nm INTEGER,
        cargo VARCHAR,
        latitude FLOAT,
        longitude FLOAT,
        altitude_ft FLOAT,
        country_code VARCHAR,
        city_name VARCHAR,
        departure_hour VARCHAR,
        departure_weather VARCHAR,
        reward INTEGER,
        user_id INTEGER,
        status VARCHAR
    );
""")
q = con.execute(query).fetchall()
print("contracts_historical table created")


query = (f"""
    CREATE SEQUENCE users_aircrafts_id_seq;

    CREATE TABLE IF NOT EXISTS users_aircrafts (
        id INTEGER PRIMARY KEY DEFAULT nextval('users_aircrafts_id_seq'),
        user_id INTEGER,
        aircraft_id INTEGER,
        aircraft_model VARCHAR,
        hangar_location VARCHAR,
        fuel_level FLOAT,
        maintenance_status VARCHAR,
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
        edition VARCHAR,
        purchase_price INTEGER
    );
""")
q = con.execute(query).fetchall()
print("users_aircrafts table created")

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
query = (f"""
    INSERT INTO users_aircrafts (user_id, aircraft_id, aircraft_model, hangar_location, fuel_level, maintenance_status, purchase_date, manufacturer, category, engine_type, max_speed_kts, cruise_speed_kts, range_nm, avg_fuel_consumption_gal_h, service_ceiling_ft, max_payload_kg, max_passengers, edition, purchase_price)
         VALUES (1, 1, 'Cessna 172 Skyhawk G1000', 'LFCH', 100, 'Operational', '2026-05-28', 'Cessna', 'General Aviation', 'Piston', 127, 122, 640, 9, 14000, 385, 4, 'Standard', 745000);
""")
# try:
q = con.execute(query).fetchall()
print("User's aircraft inserted")
# except Exception:
#     print("User's aircraft already exists")
#     pass

# Etat final
tables = con.execute("SHOW TABLES").fetchall()
print("FINAL STATE :")
print(tables)