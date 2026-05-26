import duckdb

def add_contract_accepted(contract_data, user_id):
    
    print(contract_data)
    # Connexion en mémoire
    con = duckdb.connect('\data\database.duckdb')

    query = (f"""
        INSERT INTO contracts_accepted (
            contract_category,
            destination,
            destination_category,
            distance_nm,
            cargo,
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
            '{contract_data.destination}',
            '{contract_data.destination_category}',
            {contract_data.distance_nm},
            '{contract_data.cargo}',
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
    result = con.execute(query).fetchall()
    print(result)

def get_contract_accepted(user_id):
    
    # Connexion en mémoire
    con = duckdb.connect('\data\database.duckdb')

    query = (f"""
        SELECT * FROM contracts_accepted WHERE user_id = {user_id};
    """)
    result = con.execute(query).fetchall()
    print(result)
    return result

def get_contract_accepted(user_id):
    
    # Connexion en mémoire
    con = duckdb.connect('\data\database.duckdb')

    query = (f"""
        SELECT * FROM contracts_accepted WHERE user_id = {user_id};
    """)
    result = con.execute(query).fetchall()
    print(result)
    return result

def drop_contract_accepted(user_id):
    
    # Connexion en mémoire
    con = duckdb.connect('\data\database.duckdb')

    query = (f"""
        DELETE FROM contracts_accepted WHERE user_id = {user_id};
    """)
    result = con.execute(query).fetchall()
    print(result)
    return result

def add_contract_historical(contract_data, user_id, status):
    
    # Connexion en mémoire
    con = duckdb.connect('\data\database.duckdb')

    query = (f"""
        INSERT INTO contracts_historical (
            contract_category,
            destination,
            destination_category,
            distance_nm,
            cargo,
            latitude,
            longitude,
            altitude_ft,
            country_code,
            city_name,
            departure_hour,
            departure_weather,
            reward,
            user_id,
            status
        ) VALUES (
            '{contract_data.contract_category}',
            '{contract_data.destination}',
            '{contract_data.destination_category}',
            {contract_data.distance_nm},
            '{contract_data.cargo}',
            {contract_data.latitude},
            {contract_data.longitude},
            {contract_data.altitude_ft},
            '{contract_data.country_code}',
            '{contract_data.city_name}',
            '{contract_data.departure_hour}',
            '{contract_data.departure_weather}',
            {contract_data.reward},
            {user_id},
            '{status}'
        )
    """)
    result = con.execute(query).fetchall()
    print(result)
    return result

def get_contract_historical(user_id):
    
    # Connexion en mémoire
    con = duckdb.connect('\data\database.duckdb')

    query = (f"""
        SELECT * FROM contracts_historical WHERE user_id = {user_id};
    """)
    result = con.execute(query).fetchall()
    print(result)
    return result

def get_pilot_intels(user_id):
    
    # Connexion en mémoire
    con = duckdb.connect('\data\database.duckdb')

    query = (f"""
        SELECT username, wallet, plane_model, current_location FROM users WHERE user_id = {user_id};
    """)
    result = con.execute(query).fetchall()
    print(result)
    return result

def get_pilot_location(user_id):
    
    # Connexion en mémoire
    con = duckdb.connect('\data\database.duckdb')

    query = (f"""
        SELECT current_location FROM users WHERE user_id = {user_id};
    """)
    result = con.execute(query).fetchall()
    print(result)
    return result

def income_to_wallet(user_id, income):
    
    # Connexion en mémoire
    con = duckdb.connect('\data\database.duckdb')

    query = (f"""
        UPDATE users SET wallet = wallet + {income} WHERE user_id = {user_id};
    """)
    result = con.execute(query).fetchall()
    print(result)
    return result

def expense_from_wallet(user_id, expense):
    
    # Connexion en mémoire
    con = duckdb.connect('\data\database.duckdb')

    query = (f"""
        UPDATE users SET wallet = wallet - {expense} WHERE user_id = {user_id};
    """)
    result = con.execute(query).fetchall()
    print(result)
    return result

def update_pilot_location(user_id, new_location):
    
    # Connexion en mémoire
    con = duckdb.connect('\data\database.duckdb')

    query = (f"""
        UPDATE users SET current_location = '{new_location}' WHERE user_id = {user_id};
    """)
    result = con.execute(query).fetchall()
    print(result)
    return result