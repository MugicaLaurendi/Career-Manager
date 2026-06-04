import duckdb
import math
import random
import pandas as pd
from datetime import datetime
from pathlib import Path
from math import radians, sin, cos, sqrt, asin


QUANTITY_OF_CONTRACTS = 20

CONTRACT_TYPES_TUPLE = (
        "Cargo",
        "Passenger"
    )

CONTRACT_REWARDS = {
        "Cargo": 50,
        "Passenger": 60,
        "Tourism": 40
    }

CONTRACT_TEMPLATE = [        
        'contract_category',
        'departure_airport',
        'arrival_airport',
        'arrival_airport_category',
        'distance_nm',
        'cargo',
        'informations',
        'latitude',
        'longitude',
        'altitude_ft',
        'country_code',
        'city_name',
        'departure_hour',
        'departure_weather',
        'reward',
        'user_id'
    ]


def calcul_bounding_box(lat_origine, lon_origine, distance_nm):

    # Constante absolue : 1 degré de latitude = 60 milles nautiques
    nm_par_degre_lat = 60.0

    # 1. Calcul du delta pour la latitude
    delta_lat = distance_nm / nm_par_degre_lat
    
    # 2. Calcul du delta pour la longitude (dépend de la latitude actuelle)
    # Plus on monte vers les pôles, plus les méridiens se resserrent
    delta_lon = distance_nm / (nm_par_degre_lat * math.cos(math.radians(lat_origine)))

    # 3. Calcul des coordonnées de la boîte
    lat_min = lat_origine - delta_lat
    lat_max = lat_origine + delta_lat
    lon_min = lon_origine - delta_lon
    lon_max = lon_origine + delta_lon

    return {
        "lat_min": round(lat_min, 6),
        "lat_max": round(lat_max, 6),
        "lon_min": round(lon_min, 6),
        "lon_max": round(lon_max, 6)
    }


def distance_gps(lat1, lon1, lat2, lon2):
    # Rayon moyen de la Terre en miles nautiques
    # 1 mile nautique = 1,852 km
    R = 6371.0 / 1.852   # ≈ 3440.065 NM

    # Conversion des degrés en radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Différences
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Formule de Haversine
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # Distance en miles nautiques (NM)
    return round(R * c)

def search_airport(airport_oaci):
    # Chemin du fichier CSV depuis le dossier racine du projet
    project_root = Path(__file__).resolve().parent.parent
    csv_path_airports = project_root / "data" / "airports.csv"
    if not csv_path_airports.exists():
        raise FileNotFoundError(f"Fichier introuvable : {csv_path_airports}")

    # Connexion en mémoire
    con = duckdb.connect()

    # Requête pour récupérer les coordonnées de l'aéroport d'origine
    query = (f"""
        SELECT latitude_deg, longitude_deg
        FROM read_csv_auto('{csv_path_airports.as_posix()}')
        WHERE ident = '{airport_oaci}' ;
    """)
    result_origin = con.execute(query).fetchall()
    
    if not result_origin:
        raise ValueError(f"Aéroport '{airport_oaci}' non trouvé dans la base de données")
    
    lat_aeroport, lon_aeroport = result_origin[0]

    return [(airport_oaci, lat_aeroport, lon_aeroport)]


def search_contract(airport_origin: str, contract_type_selected: list, destination_category_selected: list, dist_min: int, dist_max: int) -> pd.DataFrame:



    # Chemin du fichier CSV depuis le dossier racine du projet
    project_root = Path(__file__).resolve().parent.parent
    csv_path_airports = project_root / "data" / "airports.csv"
    if not csv_path_airports.exists():
        raise FileNotFoundError(f"Fichier introuvable : {csv_path_airports}")

    # Connexion en mémoire
    con = duckdb.connect()

    # Récupère les coordonnées de l'aéroport d'origine
    airport_origin_info = search_airport(airport_origin)
    lat_aeroport, lon_aeroport = airport_origin_info[0][1], airport_origin_info[0][2]

    # Calcule les boîtes de recherche
    box_min = calcul_bounding_box(lat_aeroport, lon_aeroport, dist_min)
    box_max = calcul_bounding_box(lat_aeroport, lon_aeroport, dist_max)

    # Construire la condition pour filtrer les catégories d'aéroport d'arrivée
    if destination_category_selected == [] :
        destination_category_condition = "1=1"  # Pas de filtre sur la catégorie d'aéroport
    else:
        list_destination_category = [f"'{cat}'" for cat in destination_category_selected]
        destination_category_condition = f"type IN ({', '.join(list_destination_category)})"
        print(destination_category_condition)

    # Requête pour récupérer les aéroports dans la zone d'anneau
    query = (f"""
        SELECT ident, type, latitude_deg, longitude_deg, elevation_ft, iso_country, municipality
        FROM read_csv_auto('{csv_path_airports.as_posix()}')
        WHERE 
        (latitude_deg BETWEEN {box_max['lat_min']} AND {box_max['lat_max']} 
         AND longitude_deg BETWEEN {box_max['lon_min']} AND {box_max['lon_max']})
        AND NOT 
        (latitude_deg BETWEEN {box_min['lat_min']} AND {box_min['lat_max']} 
         AND longitude_deg BETWEEN {box_min['lon_min']} AND {box_min['lon_max']})
         AND {destination_category_condition}
    """)
    airports_df = con.execute(query).df()


    # nombre de contrats à sélectionner par catégorie de mission
    quantity_to_select_by_category = min(QUANTITY_OF_CONTRACTS, len(airports_df)) // len(CONTRACT_TYPES_TUPLE)


    # Initilisation du datframe de contrats
    contracts_df = pd.DataFrame(data= None, columns=CONTRACT_TEMPLATE)
    print(contracts_df)
    
    # Générer des contrats pour chaque type de mission
    for contract_type in contract_type_selected:
            selected_airports = airports_df.sample(n=quantity_to_select_by_category, replace=False) if len(airports_df) >= quantity_to_select_by_category else airports_df.sample(n=quantity_to_select_by_category, replace=True)
            for id, row in selected_airports.iterrows():
                contract = pd.DataFrame([{
                    'contract_category': contract_type,
                    'departure_airport': airport_origin,
                    'arrival_airport': row['ident'],
                    'arrival_airport_category': row['type'],
                    'distance_nm': None,
                    'cargo': None,
                    'informations': None,
                    'latitude': row['latitude_deg'],
                    'longitude': row['longitude_deg'],
                    'altitude_ft': row['elevation_ft'],
                    'country_code': row['iso_country'],
                    'city_name': row['municipality'],
                    'departure_hour': None,
                    'departure_weather': None,
                    'reward': None,
                    'user_id': None
                }])
                contracts_df = pd.concat([contracts_df, contract], ignore_index=True)
    print(contracts_df)


    for index, row in contracts_df.iterrows():

            
        # -------------------------------------------------- CARGO --------------------------------------------------   
        
        if row['contract_category'] == "Cargo":
    
            # Calcul de la distance pour chaque aéroport d'arrivée
            distance = distance_gps(lat_aeroport, lon_aeroport, row['latitude'], row['longitude'])

            # calcul de la recompense pour chaque contrat
            reward = distance * CONTRACT_REWARDS[row['contract_category']]
        
            # ajout de l'heure de départ et de la météo (valeurs aléatoires)
            departure_hour = f"{random.randint(0, 23)}:{random.randint(0, 59):02d}"
            departure_weather = random.choice(["Clear", "Cloudy", "Rain", "Snow", "Fog", "Thunderstorm"])

            # ajout de la cargaison
            cargo = f"{random.randint(100, 400)} lbs"  # Quantité de cargaison en livres


        # -------------------------------------------------- PASSENGER --------------------------------------------------   

        if row['contract_category'] == "Passenger":
    
            # Calcul de la distance pour chaque aéroport d'arrivée
            distance = distance_gps(lat_aeroport, lon_aeroport, row['latitude'], row['longitude'])

            # calcul de la recompense pour chaque contrat
            reward = distance * CONTRACT_REWARDS[row['contract_category']]
        
            # ajout de l'heure de départ et de la météo (valeurs aléatoires)
            departure_hour = f"{random.randint(0, 23)}:{random.randint(0, 59):02d}"
            departure_weather = random.choice(["Clear", "Cloudy", "Rain", "Snow", "Fog", "Thunderstorm"])

            # ajout des passagers
            cargo = f" {random.randint(1, 3)} persons ({random.randint(100, 400)} lbs)"  # Nombre de passagers et poids total


        # ---------------- Mise à jour du dataframe de contrats ----------------

        contracts_df.loc[index] = {
            'contract_category': row['contract_category'],
            'departure_airport': row['departure_airport'],
            'arrival_airport': row['arrival_airport'],
            'arrival_airport_category': row['arrival_airport_category'],
            'distance_nm': distance,
            'cargo': cargo,
            'informations': row['informations'],
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'altitude_ft': row['altitude_ft'],
            'country_code': row['country_code'],
            'city_name': row['city_name'],
            'departure_hour': departure_hour,
            'departure_weather': departure_weather,
            'reward': reward,
            'user_id': row['user_id']
        }

    


    print(f"{datetime.now()} - {len(contracts_df)} contracts found from {airport_origin} with the selected criteria.")
    return contracts_df
