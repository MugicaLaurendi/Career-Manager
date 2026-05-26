import duckdb
import math
import random
import pandas as pd
from pathlib import Path
from math import radians, sin, cos, sqrt, asin

contract_type_tuple = ("All", "Cargo", "Passenger")


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


def search_contract(airport_origin, contract_type_selected, destination_category_selected, dist_min, dist_max):

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
    """)
    airports_list = con.execute(query).fetchall()

    # Appliquer un échantillonnage aléatoire pour limiter le nombre de résultats
    quantity_to_select = min(20, len(airports_list))
    selection_list = []
    
    # Filtrer par catégorie de destination si nécessaire
    if destination_category_selected != "All":
        airports_list = [airport for airport in airports_list if airport[1] == destination_category_selected]
        
    
    
    # Générer des contrats pour chaque type de mission
    for contract_type in contract_type_tuple[1:]:  # Exclure "All" 
            contracts_list = random.sample(airports_list, quantity_to_select // (len(contract_type_tuple)-1)) if len(airports_list) > quantity_to_select else airports_list
            for contract in contracts_list:
                selection_list.append(contract + (contract_type,))

    # filtrer par type de mission si nécessaire
    if contract_type_selected != "All":
        selection_list = [contract for contract in selection_list if contract[7] == contract_type_selected]
    
    # Calcul de la distance pour chaque aéroport
    for i, (ident, type, lat, lon, elevation, country, city, contract_type) in enumerate(selection_list):
        distance = distance_gps(lat_aeroport, lon_aeroport, lat, lon)
        selection_list[i] = (ident, type, lat, lon, elevation, country, city, contract_type, distance)

    contract_type_reward = {
        "Cargo": 50,
        "Passenger": 60,
        "Tourism": 40
    }

    # calcul de la recompense pour chaque contrat
    for i, (ident, type, lat, lon, elevation, country, city, contract_type, distance) in enumerate(selection_list):
        reward = distance * contract_type_reward[contract_type]

        selection_list[i] = (contract_type, ident, type, distance,lat, lon, elevation,country, city, reward)
        
    # ajout de l'heure de départ et de la météo (valeurs aléatoires)
    for i, (contract_type, ident, type, distance, lat, lon, elevation, country, city, reward) in enumerate(selection_list):
        departure_hour = f"{random.randint(0, 23)}:{random.randint(0, 59):02d}"
        departure_weather = random.choice(["Clear", "Cloudy", "Rain", "Snow", "Fog", "Thunderstorm"])

        selection_list[i] = (contract_type, ident, type, distance, lat, lon, elevation, country, city, departure_hour, departure_weather, reward)

    # ajout de la cargaison
    for i, (contract_type, ident, type, distance, lat, lon, elevation, country, city, departure_hour, departure_weather, reward) in enumerate(selection_list):
        if contract_type == "Cargo":
            cargo = f"{random.randint(100, 400)} lbs"  # Quantité de cargaison en livres
        elif contract_type == "Passenger":
            cargo = f" {random.randint(1, 3)} persons ({random.randint(100, 400)} lbs)"  # Nombre de passagers et poids total
        else:
            cargo = None

        selection_list[i] = (contract_type, ident, type, distance, cargo, lat, lon, elevation, country, city, departure_hour, departure_weather, reward)
    
    
    
    # retoune la liste des contrats
    df_contracts = pd.DataFrame(selection_list, columns=[
        "contract_category",
        "destination",
        "destination_category",
        "distance_nm",
        "cargo",
        "latitude",
        "longitude",
        "altitude_ft",
        "country_code",
        "city_name",
        "departure_hour",
        "departure_weather",
        "reward"])

    return df_contracts
