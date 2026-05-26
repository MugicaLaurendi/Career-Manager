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
q1 = con.execute(query).fetchall()
print(q1)

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
q2 = con.execute(query).fetchall()
print(q2)

query = (f"""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username VARCHAR,
        wallet INTEGER,
        plane_model VARCHAR,
        current_location VARCHAR
    );
""")
q3 = con.execute(query).fetchall()
print(q3)

query = (f"""
    INSERT INTO users (user_id, username, wallet, plane_model, current_location) VALUES (1, 'Laurendi Mugica', 10000, 'Cessna 172', 'LFCH');
""")
q4 = con.execute(query).fetchall()
print(q4)

# Etat final
tables = con.execute("SHOW TABLES").fetchall()
print("FINAL STATE :")
print(tables)