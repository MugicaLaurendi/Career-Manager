import streamlit as st
import pandas as pd
from datetime import datetime

from scripts.search_contract import search_airport
from scripts.database_requests import get_user_location

from tabs import sidebar, contracts, flight, hangar, shop, bank, login

# Configuration de la page pour qu'elle prenne toute la largeur
st.set_page_config(layout="wide", page_title="Career Manager", page_icon="✈️", initial_sidebar_state="expanded")

# CSS
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# Authentification (sélection de profil, sans mot de passe)

if "user_id" not in st.session_state:

    col1, col2, col3 = st.columns(3)

    with col2:
        st.header("Career Manager ")
        login.render()
        st.stop()

user_id = st.session_state.user_id

# Initialiser les variables

if "airport_origin_info" not in st.session_state:
    st.session_state.airport_origin_info = search_airport(get_user_location(user_id).loc[0, 'current_location'])
if "df_contracts" not in st.session_state:
    st.session_state.df_contracts = pd.DataFrame({"contract_category": [],
        "departure_airport": [],
        "arrival_airport": [],
        "arrival_airport_category": [],
        "distance_nm": [],
        "cargo": [],
        "informations": [],
        "latitude": [],
        "longitude": [],
        "altitude_ft": [],
        "country_code": [],
        "city_name": [],
        "departure_hour": [],
        "departure_weather": [],
        "reward": []})
if "dest_ff_lat" not in st.session_state:
    st.session_state.dest_ff_lat = 0
if "dest_ff_lon" not in st.session_state:
    st.session_state.dest_ff_lon = 0

# Titre de la page
st.header("✈️  Career Manager ")

with st.sidebar:
    sidebar.render(user_id)

contracts_tab, flight_tab, hangar_tab, shop_tab, bank_tab = st.tabs(["📫  Contracts", "✈️  Flight", "🔧  Hangar", "🛒  Shop", "🏦  Bank"])

with contracts_tab:
    airport_origin, center_lat, center_lon = contracts.render(user_id)

with flight_tab:
    flight.render(user_id, airport_origin, center_lat, center_lon)

with hangar_tab:
    hangar.render(user_id)

with shop_tab:
    shop.render(user_id)

with bank_tab:
    bank.render(user_id)
