import streamlit as st
import folium
import pandas as pd
from types import SimpleNamespace
from streamlit_folium import st_folium
import time

from scripts.search_contract import search_contract, search_airport
from scripts.search_contract import contract_type_tuple
from scripts.database_requests import *

# Configuration de la page pour qu'elle prenne toute la largeur
st.set_page_config(layout="wide", page_title="Career Manager", page_icon="✈️",initial_sidebar_state="expanded")

# CSS
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# Initialiser les variables

user_id = 1  # ID de l'utilisateur (à remplacer par une authentification réelle)

contract_columns = ["contract_category", "destination", "destination_category", "distance_nm", "cargo", "latitude", "longitude", "altitude_ft", "country_code", "city_name", "departure_hour", "departure_weather", "reward"]

if "airport_origin_info" not in st.session_state:
    st.session_state.airport_origin_info = search_airport(get_pilot_location(user_id)[0][0])
if "df_contracts" not in st.session_state:
    st.session_state.df_contracts = pd.DataFrame({"contract_category": [],
        "destination": [],
        "destination_category": [],
        "distance_nm": [],
        "cargo": [],
        "latitude": [],
        "longitude": [],
        "altitude_ft": [],
        "country_code": [],
        "city_name": [],
        "departure_hour": [],
        "departure_weather": [],
        "reward": []})

# Titre de la page
st.header("✈️  Career Manager ")

        
contracts_tab, hangar_tab, shop_tab = st.tabs(["✉︎ Contracts","🛠  Hangar", "$  Shop"])

# ----- TABLEAU DES CONTRATS -----
with contracts_tab:

    col_sidebar, col_content = st.columns([1,3])

    # --- MENU LATÉRAL (SIDEBAR) ---
    with col_sidebar:
        


        airport_origin = st.text_input("Aeroport de depart (OACI)", get_pilot_location(user_id)[0][0])
        if st.button("Search airport", width="stretch"):
            try:
                airport_origin_info = search_airport(airport_origin)
                st.session_state.airport_origin_info = airport_origin_info
            except Exception as e:
                st.error(f"Erreur : {str(e)}")

        contract_type_selected = st.selectbox(
            "Contract category:",
            contract_type_tuple
        )

        destination_category_selected = st.selectbox(
            "Destination category:",
            ("All", "small_airport", "medium_airport", "large_airport", "heliport", "seaplane_base")
        )

        dist_min = st.number_input("Distance min", value=50)
        dist_max = st.number_input("Distance max", value=100)

        if st.button("Search contracts", width="stretch"):
            try:
                # Recherche des contrats
                print(f"Recherche de contrats pour l'aéroport {airport_origin} a une distance entre {dist_min} et {dist_max}")
                df_contracts = search_contract(airport_origin, contract_type_selected, destination_category_selected, dist_min, dist_max)

                st.session_state.df_contracts = df_contracts
                st.success(f"{len(df_contracts)} contract(s) found")
            except Exception as e:
                st.error(f"Erreur : {str(e)}")


    # --- CONTENU PRINCIPAL ---
    with col_content:

        # Filtres

        df_contracts_filtered = st.session_state.df_contracts

        # --- CARTE FOLIUM ---

        # Création de la carte avec les aéroports
        if st.session_state.airport_origin_info:
            # Utiliser les coordonnées du premier aéroport comme centre
            center_lat = st.session_state.airport_origin_info[0][1]
            center_lon = st.session_state.airport_origin_info[0][2]
        else:
            # Coordonnées par défaut (Paris)
            center_lat = 48.8566
            center_lon = 2.3522

        # Créer la carte
        style_carte = "OpenStreetMap"
        m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles=style_carte)

        # Ajouter le marqueur de l'aéroport d'origine (avec couleur différente)
        folium.Marker(
            location=[center_lat, center_lon],
            popup=f"OACI: {airport_origin}, Lat: {center_lat}, Lon: {center_lon}",
            icon=folium.Icon(color="green", icon="plane")
        ).add_to(m)


        if df_contracts_filtered is not None and not df_contracts_filtered.empty:

                for contract in df_contracts_filtered.itertuples(index=True):

                        # Ajouter un marqueur pour chaque contrat
                        if contract.contract_category == "Cargo":
                            icon_color = "blue"
                            icon_logo = "book"
                        elif contract.contract_category == "Passenger":
                            icon_color = "pink"
                            icon_logo = "user"
                        elif contract.contract_category == "Tourism":
                            icon_color = "orange"
                            icon_logo = "camera"
                        else:
                            icon_color = "gray"
                            icon_logo = "question"

                        folium.Marker(
                            location=[contract.latitude, contract.longitude],
                            tooltip=f"OACI: {contract.destination}</br> Contract ID: {contract[0]}</br> Distance: {contract.distance_nm} nm</br> Reward: ${contract.reward}",
                            icon=folium.Icon(color=icon_color, icon=icon_logo)
                        ).add_to(m)

                        # Ajout de la ligne reliant les deux points
                        folium.PolyLine(
                            locations=[(center_lat, center_lon), (contract.latitude, contract.longitude)],
                            color="black",
                            weight=2,
                            opacity=0.5,
                            dash_array="10, 10"
                        ).add_to(m)

        # Affichage de la carte
        st_folium(m, width="100%", height=400, use_container_width=False)

        col1, col2 = st.columns(2)

        # ----- TABLEAU DES CONTRATS -----

        with col1:

            contract_selection = st.dataframe(df_contracts_filtered[[ "contract_category", "destination", "distance_nm", "reward" ]], hide_index=False, on_select="rerun" ,selection_mode="single-row", column_config={"reward": st.column_config.NumberColumn("Reward", format="$ %,d")})


        # ----- DÉTAILS DU CONTRAT SÉLECTIONNÉ -----
        with col2:
            with st.container(border=True):
                # Vérifier si une ligne est sélectionnée
                if contract_selection.selection.rows:
                    # Récupérer l'index de la ligne sélectionnée
                    selected_index = contract_selection.selection.rows[0]

                    # Extraire la ligne correspondante
                    selected_row = df_contracts_filtered.iloc[selected_index]

                    # Afficher les détails ailleurs dans la page
                    st.subheader("Contract details")
                    st.markdown(f"**OACI :** {selected_row['destination']}")
                    st.markdown(f"**Category :** {selected_row['contract_category']}")
                    st.markdown(f"**Distance :** {selected_row['distance_nm']} nm")
                    st.markdown(f"**country :** {selected_row['country_code']}")
                    st.markdown(f"**city :** {selected_row['city_name']}")
                    st.markdown(f"**Cargo :** {selected_row['cargo']}")
                    st.markdown(f"**Departure hour :** {selected_row['departure_hour']}")
                    st.markdown(f"**Departure weather :** {selected_row['departure_weather']}")
                    st.markdown(f"**Reward :** $ {selected_row['reward']:,}".replace(',', ' '))

                    if st.button("Accept contract", width="stretch"):
                        if get_contract_accepted(user_id) and len(get_contract_accepted(user_id)) > 0:
                            st.warning("You already have an accepted contract. Please complete or abort it before accepting a new one.", icon="⚠️")
                        else:
                            drop_contract_accepted(user_id)
                            add_contract_accepted(selected_row, user_id)
                            st.info("Contract accepted", icon="✅")

                else:
                    st.write("ⓘ  Sélectionnez un contrat dans le tableau.")
                
    
with hangar_tab:
    
    col_intels, col_contracts  = st.columns([1,1])
    
    with col_intels :
        
        with st.container(border=True):
            
            pilot_intels = pd.DataFrame(get_pilot_intels(user_id), columns=["username", "wallet", "plane_model", "current_location"])
            st.subheader("Pilot informations")
            
            if not pilot_intels.empty:
                st.markdown(f"**Username :** {pilot_intels.iloc[0][0]}")
                st.markdown(f"**Wallet :** $ {pilot_intels.iloc[0][1]:,}".replace(',', ' '))
                st.markdown(f"**Plane model :** {pilot_intels.iloc[0][2]}")
                st.markdown(f"**Current location :** {pilot_intels.iloc[0][3]}")
            else:
                st.markdown("**Username :** -")
                st.markdown("**Wallet :** $ 0")
                st.markdown("**Plane model :** -")
                st.markdown("**Current location :** -")

        st.subheader("Hangar")
        historic_contracts = st.dataframe()
        
    with col_contracts :
        
        with st.container(border=True):
            
            contract = pd.DataFrame(get_contract_accepted(user_id), columns=contract_columns + ["user_id"])
            
            if contract is not None and not contract.empty:
                contract_obj = SimpleNamespace(**contract.iloc[0].to_dict())
                
                st.subheader("Current contract")
                st.markdown(f"**OACI :** {contract_obj.destination}")
                st.markdown(f"**Category :** {contract_obj.contract_category}")
                st.markdown(f"**Distance :** {contract_obj.distance_nm} nm")
                st.markdown(f"**country :** {contract_obj.country_code}")
                st.markdown(f"**city :** {contract_obj.city_name}")
                st.markdown(f"**Cargo :** {contract_obj.cargo}")
                st.markdown(f"**Departure hour :** {contract_obj.departure_hour}")
                st.markdown(f"**Departure weather :** {contract_obj.departure_weather}")
                st.markdown(f"**Reward :** $ {contract_obj.reward}")

                left, right = st.columns(2)

                # Boutons pour compléter le contrat
                if left.button("Completed",type="primary", width="stretch"):
                    add_contract_historical(contract_obj, user_id, "completed")
                    income_to_wallet(user_id, contract_obj.reward)
                    update_pilot_location(user_id, contract_obj.destination)
                    st.info("Contract completed", icon="✅")
                    time.sleep(5)
                    contract = 0
                    drop_contract_accepted(user_id)
                    st.rerun()

                # Bouton pour annuler le contrat
                if right.button("Abort", type="secondary", width="stretch"):
                    add_contract_historical(contract_obj, user_id, "aborted")
                    st.warning("Contract aborted", icon="❌")
                    time.sleep(5)
                    contract = 0
                    drop_contract_accepted(user_id)
                    st.rerun()
            else:
                st.subheader("Current contract")
                st.write("ⓘ  Aucun contrat accepté pour le moment.")
        
        st.subheader("Historic")
        historic_contracts_df = pd.DataFrame(get_contract_historical(user_id), columns=contract_columns +["user_id"] +["status"])
        historic_contracts = st.dataframe(historic_contracts_df[[ "status", "reward", "contract_category", "destination", "destination_category", "distance_nm", "cargo", "latitude", "longitude", "altitude_ft", "country_code", "city_name", "departure_hour", "departure_weather" ]], hide_index=True)

    
with shop_tab:
    
    col_list, col_info  = st.columns([1,1])
    
    with col_list :
        
        aircraft_selection = st.dataframe({"test": ["test1", "test2"]})
        
    with col_info :
        
        with st.container(border=True):
            
            st.write("ⓘ  Select an aircraft in the table.")
            
            # if aircraft_selection.selection.rows:
            #     st.subheader("Informations")
                
            # else:
            #     st.write("ⓘ  Select an aircraft in the table.")
        