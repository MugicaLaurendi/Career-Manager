import duckdb
import pandas as pd
import time
from pathlib import Path
from datetime import datetime


DATABASE_PATH = '\data\database.duckdb'


def add_contract_accepted(contract_data, user_id):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        INSERT INTO contracts_accepted (
            contract_category,
            departure_airport,
            arrival_airport,
            arrival_airport_category,
            distance_nm,
            cargo,
            informations,
            latitude,
            longitude,
            altitude_ft,
            country_code,
            city_name,
            departure_hour,
            departure_weather,
            reward,
            user_id
        ) VALUES (
            '{contract_data.contract_category}',
            '{contract_data.departure_airport}',
            '{contract_data.arrival_airport}',
            '{contract_data.arrival_airport_category}',
            {contract_data.distance_nm},
            '{contract_data.cargo}',
            '{contract_data.informations}',
            {contract_data.latitude},
            {contract_data.longitude},
            {contract_data.altitude_ft},
            '{contract_data.country_code}',
            '{contract_data.city_name}',
            '{contract_data.departure_hour}',
            '{contract_data.departure_weather}',
            {contract_data.reward},
            {user_id}
        )
    """)
    result = con.execute(query).df()
    print(f"{datetime.now()} - Contract added for user {user_id}")

def get_contract_accepted(user_id):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        SELECT * FROM contracts_accepted WHERE user_id = {user_id};
    """)
    result = con.execute(query).df()
    return result

def get_contract_accepted(user_id):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        SELECT * FROM contracts_accepted WHERE user_id = {user_id};
    """)
    result = con.execute(query).df()
    return result

def drop_contract_accepted(user_id):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        DELETE FROM contracts_accepted WHERE user_id = {user_id};
    """)
    result = con.execute(query).df()
    return result

def add_contract_historical(contract_data, user_id, status):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    # Extract the first row if contract_data is a DataFrame
    if hasattr(contract_data, 'iloc'):
        contract_data = contract_data.iloc[0]

    query = (f"""
        INSERT INTO contracts_historical (
            contract_category,
            departure_airport,
            arrival_airport,
            arrival_airport_category,
            distance_nm,
            cargo,
            informations,
            latitude,
            longitude,
            altitude_ft,
            country_code,
            city_name,
            departure_hour,
            departure_weather,
            reward,
            user_id,
            status,
            date
        ) VALUES (
            '{contract_data['contract_category']}',
            '{contract_data['departure_airport']}',
            '{contract_data['arrival_airport']}',
            '{contract_data['arrival_airport_category']}',
            {contract_data['distance_nm']},
            '{contract_data['cargo']}',
            '{contract_data['informations']}',
            {contract_data['latitude']},
            {contract_data['longitude']},
            {contract_data['altitude_ft']},
            '{contract_data['country_code']}',
            '{contract_data['city_name']}',
            '{contract_data['departure_hour']}',
            '{contract_data['departure_weather']}',
            '{contract_data['reward']}',
            {user_id},
            '{status}',
            '{datetime.now()}'
        )
    """)
    result = con.execute(query).df()
    return result

def get_contract_historical(user_id):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        SELECT * FROM contracts_historical WHERE user_id = {user_id};
    """)
    result = con.execute(query).df()
    return result

def get_user_intels(user_id):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        SELECT username, wallet, current_aircraft, current_location FROM users WHERE id = {user_id};
    """)
    result = con.execute(query).df()
    return result

def get_user_location(user_id):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        SELECT current_location FROM users WHERE id = {user_id};
    """)
    result = con.execute(query).df()
    return result

def income_to_wallet(user_id, income):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        UPDATE users SET wallet = wallet + {income} WHERE id = {user_id};
    """)
    result = con.execute(query).df()
    print(f"{datetime.now()} - Updating wallet for user {user_id}: + {income} $")
    return result

def expense_from_wallet(user_id, expense):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        UPDATE users SET wallet = wallet - {expense} WHERE id = {user_id};
    """)
    result = con.execute(query).df()
    print(f"{datetime.now()} - Updating wallet for user {user_id}: - {expense} $")
    return result

def update_user_location(user_id, new_location):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        UPDATE users SET current_location = '{new_location}' WHERE id = {user_id};
    """)
    result = con.execute(query).df()
    print(f"{datetime.now()} - Location updated for user {user_id}: {new_location}")
    return result

def update_user_current_aircraft(user_id, new_aircraft):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        UPDATE users SET current_aircraft = '{new_aircraft}' WHERE id = {user_id};
    """)
    result = con.execute(query).df()
    print(f"{datetime.now()} - Aircraft updated for user {user_id}: {new_aircraft}")
    return result

def get_users_aircrafts_name(user_id,aircraft_id):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        SELECT aircraft_model FROM users_aircrafts WHERE user_id = {user_id} AND id = {aircraft_id};
    """)
    result = con.execute(query).df()
    return result

def get_user_current_aircraft(user_id):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        SELECT
            users_aircrafts.aircraft_model,
            users_aircrafts.fuel_level,
            users_aircrafts.maintenance_level,
            users_aircrafts.purchase_date,
            users_aircrafts.purchase_price,
            users_aircrafts.manufacturer,
            users_aircrafts.category,
            users_aircrafts.engine_type,
            users_aircrafts.max_speed_kts,
            users_aircrafts.cruise_speed_kts,
            users_aircrafts.range_nm,
            users_aircrafts.avg_fuel_consumption_gal_h,
            users_aircrafts.service_ceiling_ft,
            users_aircrafts.max_payload_kg,
            users_aircrafts.max_passengers,
            users_aircrafts.edition
        FROM users_aircrafts
        INNER JOIN users ON users_aircrafts.id = users.current_aircraft
        WHERE users.id = {user_id};
    """)
    result = con.execute(query).df()
    return result

def get_users_aircrafts(user_id):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        SELECT id, aircraft_model, hangar_location, fuel_level, maintenance_level, purchase_price, purchase_date FROM users_aircrafts WHERE user_id = {user_id};
    """)
    result = con.execute(query).df()
    return result

def add_user_aircraft(user_id: int, aircraft_location: str, aircraft_data: pd.Series):
    
    # Connexion en mémoire
    con = duckdb.connect(DATABASE_PATH)

    query = (f"""
        INSERT INTO users_aircrafts (
            user_id,
            aircraft_model,
            hangar_location,
            fuel_level,
            maintenance_level,
            purchase_date,
            manufacturer,
            category,
            engine_type,
            max_speed_kts,
            cruise_speed_kts,
            range_nm,
            avg_fuel_consumption_gal_h,
            service_ceiling_ft,
            max_payload_kg,
            max_passengers,
            edition,
            purchase_price
        ) VALUES (
            {user_id},
            '{aircraft_data['name']}',
            '{aircraft_location}',
            100,  -- Assuming new aircraft starts with full fuel
            100,  -- Assuming new aircraft starts with full maintenance level
            DATE '{datetime.now().date()}',  -- Assuming purchase date is the current date
            '{aircraft_data['manufacturer']}',
            '{aircraft_data['category']}',
            '{aircraft_data['engine_type']}',
            {aircraft_data['max_speed_kts']},
            {aircraft_data['cruise_speed_kts']},
            {aircraft_data['range_nm']},
            {aircraft_data['avg_fuel_consumption_gal_h']},
            {aircraft_data['service_ceiling_ft']},
            {aircraft_data['max_payload_kg']},
            {aircraft_data['max_passengers']},
            '{aircraft_data['edition']}',
            {aircraft_data['price_usd']}
        )
    """)
    result = con.execute(query).df()
    print(f"{datetime.now()} - Aircraft '{aircraft_data['name']}' added to user {user_id}'s collection at location {aircraft_location}")

def check_airport_location(airport_oaci):
    # Chemin du fichier CSV depuis le dossier racine du projet
    project_root = Path(__file__).resolve().parent.parent
    csv_path_airports = project_root / "data" / "airports.csv"
    if not csv_path_airports.exists():
        raise FileNotFoundError(f"Fichier introuvable : {csv_path_airports}")

    # Connexion en mémoire
    con = duckdb.connect()

    # Requête pour vérifier l'existence de l'aéroport
    query = (f"""
        SELECT COUNT(*) 
        FROM read_csv_auto('{csv_path_airports.as_posix()}')
        WHERE ident = '{airport_oaci}' ;
    """)
    result = con.execute(query).df()

    if result[0][0] > 0:
        print(f"{datetime.now()} - Airport '{airport_oaci}' found in database.")
        return True # Retourne True si l'aéroport existe, sinon False
    else:
        print(f"{datetime.now()} - Airport '{airport_oaci}' NOT found in database.")
        return False
    
def get_airport_location(airport_oaci):
    # Chemin du fichier CSV depuis le dossier racine du projet
    project_root = Path(__file__).resolve().parent.parent
    csv_path_airports = project_root / "data" / "airports.csv"
    if not csv_path_airports.exists():
        raise FileNotFoundError(f"Fichier introuvable : {csv_path_airports}")

    # Connexion en mémoire
    con = duckdb.connect()

    # Requête pour vérifier l'existence de l'aéroport
    query = (f"""
        SELECT "latitude_deg","longitude_deg"
        FROM read_csv_auto('{csv_path_airports.as_posix()}')
        WHERE ident = '{airport_oaci}' ;
    """)
    result = con.execute(query).df()

    if result.empty:
        print(f"{datetime.now()} - Airport '{airport_oaci}' NOT found in database.")
        return []
    else:
        print(f"{datetime.now()} - Airport '{airport_oaci}' found in database.")
        return [result.loc[0,"latitude_deg"], result.loc[0,"longitude_deg"]]