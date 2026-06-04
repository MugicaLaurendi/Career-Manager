import streamlit as st
import folium
import pandas as pd
from types import SimpleNamespace
from streamlit_folium import st_folium
import time
from datetime import datetime

from scripts.search_contract import search_contract, search_airport
from scripts.search_contract import CONTRACT_TYPES_TUPLE

from scripts.database_requests import *

print(f"{datetime.now()} ----------------- Application started --------------------")

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

contract_columns = ["contract_category", "departure_airport", "arrival_airport", "arrival_airport_category", "distance_nm", "cargo", "informations", "latitude", "longitude", "altitude_ft", "country_code", "city_name", "departure_hour", "departure_weather", "reward"]

if "airport_origin_info" not in st.session_state:
    st.session_state.airport_origin_info = search_airport(get_user_location(user_id).loc[0,'current_location'])
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

        
contracts_tab, flight_tab, hangar_tab, shop_tab, bank_tab = st.tabs(["📫  Contracts", "✈️  Flight", "🔧  Hangar", "🛒  Shop", "🏦  Bank"])

# ----- TABLEAU DES CONTRATS -----
with contracts_tab:

    col_sidebar, col_content = st.columns([1,3])

    # --- MENU LATÉRAL (SIDEBAR) ---
    with col_sidebar:
        


        airport_origin = st.text_input("Aeroport de depart (OACI)", get_user_location(user_id).loc[0, 'current_location'])
        if st.button("Search airport", width="stretch"):
            try:
                airport_origin_info = search_airport(airport_origin)
                st.session_state.airport_origin_info = airport_origin_info
            except Exception as e:
                st.error(f"Erreur : {str(e)}")


        contract_type_selected = st.multiselect(
            "Contract category:",
            CONTRACT_TYPES_TUPLE,
            default=CONTRACT_TYPES_TUPLE
        )

        destination_category_tuple = ("small_airport", "medium_airport", "large_airport", "heliport", "seaplane_base")

        destination_category_selected = st.multiselect(
            "Destination category:",
            destination_category_tuple,
            default=destination_category_tuple
        )

        dist_min = st.number_input("Distance min", value=50,step=100)
        dist_max = st.number_input("Distance max", value=100,step=100)

        if st.button("Search contracts",type="primary" , width="stretch"):
            try:
                # Recherche des contrats
                print(f"{datetime.now()} - Search contracts for airport {airport_origin} with a distance between {dist_min} and {dist_max}")
                df_contracts = search_contract(airport_origin, contract_type_selected, destination_category_selected, dist_min, dist_max)

                st.session_state.df_contracts = df_contracts
                st.success(f"{len(df_contracts)} contract(s) found")
                time.sleep(2)
            except Exception as e:
                st.error(f"Erreur : {str(e)}")


    # --- CONTENU PRINCIPAL ---
    with col_content:

        df_contracts = st.session_state.df_contracts

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


        if df_contracts is not None and not df_contracts.empty:

                for index,contract in df_contracts.iterrows():

                        # Ajouter un marqueur pour chaque contrat
                        if contract['contract_category'] == "Cargo":
                            icon_color = "blue"
                            icon_logo = "book"
                        elif contract['contract_category'] == "Passenger":
                            icon_color = "pink"
                            icon_logo = "user"
                        elif contract['contract_category'] == "Tourism":
                            icon_color = "orange"
                            icon_logo = "camera"
                        else:
                            icon_color = "gray"
                            icon_logo = "question"

                        folium.Marker(
                            location=[contract['latitude'], contract['longitude']],
                            tooltip=f"OACI: {contract['arrival_airport']}</br> Contract ID: {index}</br> Distance: {contract['distance_nm']} nm</br> Reward: ${contract['reward']}",
                            icon=folium.Icon(color=icon_color, icon=icon_logo)
                        ).add_to(m)

                        # Ajout de la ligne reliant les deux points
                        folium.PolyLine(
                            locations=[(center_lat, center_lon), (contract['latitude'], contract['longitude'])],
                            color="black",
                            weight=2,
                            opacity=0.5,
                            dash_array="10, 10"
                        ).add_to(m)

        # Affichage de la carte
        st_folium(m, width="100%", height=400, use_container_width=False, key="map_available_contracts")

        col1, col2 = st.columns([2,1])

        # ----- TABLEAU DES CONTRATS -----

        with col1:

            contract_selection = st.dataframe(df_contracts[[ "contract_category","departure_airport" ,"arrival_airport", "distance_nm", "reward" ]], hide_index=False, on_select="rerun" ,selection_mode="single-row", column_config={"reward": st.column_config.NumberColumn("Reward", format="$ %,d")})


        # ----- DÉTAILS DU CONTRAT SÉLECTIONNÉ -----
        with col2:
            with st.container(border=True):
                # Vérifier si une ligne est sélectionnée
                if contract_selection.selection.rows:
                    # Récupérer l'index de la ligne sélectionnée
                    selected_index = contract_selection.selection.rows[0]

                    # Extraire la ligne correspondante
                    selected_row = df_contracts.iloc[selected_index]

                    # Afficher les détails ailleurs dans la page
                    st.subheader("Contract details")


                    with st.container(border=True,width="content",gap="xxlarge"):

                        st.markdown(f"**{selected_row['departure_airport']}** ➜  **{selected_row['arrival_airport']}**")


                    col_1, col_2 = st.columns(2)

                    with col_1:
                        st.markdown(f"**Category :** {selected_row['contract_category']}")
                        st.markdown(f"**Distance :** {selected_row['distance_nm']} nm")
                        st.markdown(f"**country :** {selected_row['country_code']}")
                        st.markdown(f"**city :** {selected_row['city_name']}")

                    with col_2:
                        st.markdown(f"**Cargo :** {selected_row['cargo']}")
                        st.markdown(f"**Departure hour :** {selected_row['departure_hour']}")
                        st.markdown(f"**Departure weather :** {selected_row['departure_weather']}")
                        st.markdown(f"**Reward :** $ {selected_row['reward']:,}".replace(',', ' '))
                    
                    st.markdown(f"**Informations :**")
                    st.markdown(f"{selected_row['informations']}")

                    @st.dialog("Are you sure you want to accept this contract?",width="medium")
                    def confirm_accept():
                        st.write(f"You are about to accept the contract to {selected_row['arrival_airport']} with a reward of $ {selected_row['reward']:,}".replace(',', ' '))
                        col_1, col_2 = st.columns(2)
                        with col_1:
                            if st.button("Confirm", type="primary",width="stretch"):
                                if get_contract_accepted(user_id).empty == False:
                                    st.warning("You already have an accepted contract. Please complete or abort it before accepting a new one.", icon="⚠️",width="stretch")
                                else:
                                    drop_contract_accepted(user_id)
                                    add_contract_accepted(selected_row, user_id)
                                    st.success("Contract accepted",width="stretch")
                                    time.sleep(2)
                                    st.rerun()
                        with col_2:
                            if st.button("Decline", type="secondary",width="stretch"):
                                st.rerun()

                    if st.button("Accept contract",type="primary", width="stretch"):
                        confirm_accept()

                else:
                    st.write("ⓘ  Sélectionnez un contrat dans le tableau.")

with flight_tab:

        col_free_flight, col_contracts  = st.columns([1,3])

        with col_free_flight:

            with st.container(border=True):

                st.subheader("Free flight")

                
                # Créer la carte
                style_carte = "OpenStreetMap"
                m_free_flight = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles=style_carte)

                # Ajouter le marqueur de l'aéroport d'origine (avec couleur différente)
                folium.Marker(
                    location=[center_lat, center_lon],
                    popup=f"OACI: {airport_origin}, Lat: {center_lat}, Lon: {center_lon}",
                    icon=folium.Icon(color="green", icon="plane")
                ).add_to(m_free_flight)
                
                if st.session_state.dest_ff_lat != 0 and st.session_state.dest_ff_lat != 0 :
                    
                    folium.Marker(
                        location=[st.session_state.dest_ff_lat, st.session_state.dest_ff_lon],
                        icon=folium.Icon(color="green", icon="arrow-down")
                    ).add_to(m_free_flight)

                    # Ajout de la ligne reliant les deux points
                    folium.PolyLine(
                        locations=[(center_lat, center_lon), (st.session_state.dest_ff_lat, st.session_state.dest_ff_lon)],
                        color="black",
                        weight=2,
                        opacity=0.5,
                        dash_array="10, 10"
                    ).add_to(m_free_flight)
                
                # Affichage de la carte
                st_folium(m_free_flight, width="100%", height=400, use_container_width=False, key="map_free_flight")

                st.write(f"Current location : **{get_user_location(user_id).loc[0, 'current_location']}**")
                dest_ff_coo = []
                airport_destination_ff = st.text_input("Select a destination (OACI) :",key='free_flight_input')
                if st.button("Search destination"):
                    dest_ff_coo = get_airport_location(airport_destination_ff)
                    if dest_ff_coo == []:
                        st.warning("No destination selected")
                    else:
                        st.session_state.dest_ff_lat = dest_ff_coo[0]
                        st.session_state.dest_ff_lon = dest_ff_coo[1]
                        st.rerun()
                     
                if st.button(f"Flight to destination ",type="primary", width="stretch"):
                    if st.session_state.dest_ff_lat == 0 and st.session_state.dest_ff_lon == 0 :
                        st.warning("No destination selected")
                    elif airport_destination_ff != '':
                        update_user_location(user_id,airport_destination_ff)
                        st.success(f"You have moved to {airport_destination_ff}")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.warning("No destination selected")

        with col_contracts :
        
            with st.container(border=True):
            
                st.session_state.contract = get_contract_accepted(user_id)
                contract = st.session_state.contract

                if contract is not None and not contract.empty:

                    col_contract_intels, col_contract_map = st.columns([1,2])

                    with col_contract_intels:
                    
                        
                        st.subheader("Current contract")

                        with st.container(border=True, width="content"):
                            st.markdown(f"**{contract.loc[0,'departure_airport']}**  ➜  **{contract.loc[0,'arrival_airport']}**")

                        st.markdown(f"**Category :** {contract.loc[0,'contract_category']}")
                        st.markdown(f"**Distance :** {contract.loc[0,'distance_nm']} nm")
                        st.markdown(f"**country :** {contract.loc[0,'country_code']}")
                        st.markdown(f"**city :** {contract.loc[0,'city_name']}")
                        st.markdown(f"**Cargo :** {contract.loc[0,'cargo']}")
                        st.markdown(f"**Departure hour :** {contract.loc[0,'departure_hour']}")
                        st.markdown(f"**Departure weather :** {contract.loc[0,'departure_weather']}")
                        st.markdown(f"**Reward :** $ {contract.loc[0,'reward']}")

                        left, right = st.columns(2)


                        @st.dialog("Confirm that the contract is completed",width="medium")
                        def confirm_complete():
                            st.info(f"You are about to complete the contract", icon="ℹ️")
                            col_1, col_2 = st.columns(2)
                            with col_1:
                                if st.button("Confirm", type="primary",width="stretch"):
                                    if get_contract_accepted(user_id).empty == False:
                                        add_contract_historical(st.session_state.contract, user_id, "completed")
                                        income_to_wallet(user_id, st.session_state.contract.loc[0,'reward'])
                                        update_user_location(user_id, st.session_state.contract.loc[0,'arrival_airport'])
                                        st.success("Contract completed", width="stretch")
                                        time.sleep(2)
                                        st.session_state.contract = 0
                                        drop_contract_accepted(user_id)
                                        st.rerun()
                            with col_2:
                                if st.button("Decline", type="secondary",width="stretch"):
                                    st.rerun()

                        @st.dialog("Confirm the abort of the contract",width="medium")
                        def confirm_abort():
                            st.warning(f"You are about to abort the contract", icon="⚠️")
                            col_1, col_2 = st.columns(2)
                            with col_1:
                                if st.button("Confirm", type="primary",width="stretch"):
                                    add_contract_historical(st.session_state.contract, user_id, "aborted")
                                    st.warning("Contract aborted")
                                    time.sleep(2)
                                    st.session_state.contract = 0
                                    drop_contract_accepted(user_id)
                                    st.rerun()
                            with col_2:
                                if st.button("Decline", type="secondary",width="stretch"):
                                    st.rerun()


                        # Boutons pour compléter le contrat
                        if left.button("Completed",type="primary", width="stretch"):
                            confirm_complete()

                        # Bouton pour annuler le contrat
                        if right.button("Abort", type="secondary", width="stretch"):
                            confirm_abort()


                    with col_contract_map:

                        if contract is not None and not contract.empty:
                            # Créer la carte centrée sur l'aéroport de départ
                            style_carte = "OpenStreetMap"
                            m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles=style_carte)


                            # Ajouter le marqueur de l'aéroport d'origine (avec couleur différente)
                            folium.Marker(
                                location=[center_lat, center_lon],
                                popup=f"OACI: {airport_origin}, Lat: {center_lat}, Lon: {center_lon}",
                                icon=folium.Icon(color="green", icon="plane")
                            ).add_to(m)

                            # Ajouter un marqueur pour la destination
                            folium.Marker(
                                location=[contract.loc[0,'latitude'], contract.loc[0,'longitude']],
                                tooltip=f"OACI: {contract['arrival_airport'].iloc[0]}</br> Contract ID: {contract.iloc[0, 0]}</br> Distance: {contract['distance_nm'].iloc[0]} nm</br> Reward: ${contract['reward'].iloc[0]}",
                                icon=folium.Icon(color="blue", icon="book")
                            ).add_to(m)

                            # Ajout de la ligne reliant les deux points
                            folium.PolyLine(
                                locations=[(center_lat, center_lon), (contract.loc[0,'latitude'], contract.loc[0,'longitude'])],
                                color="black",
                                weight=2,
                                opacity=0.5,
                                dash_array="10, 10"
                            ).add_to(m)

                            # Affichage de la carte
                            st_folium(m, width="100%", height=500, use_container_width=False, key="map_current_contract")
                        else:
                            st.subheader("Destination map")
                            st.write("ⓘ  Aucune destination à afficher pour le moment.")
                    
                else:
                    st.subheader("Current contract")
                    st.write("ⓘ  Aucun contrat accepté pour le moment.")
            
            st.subheader("Historic")

            historic_contracts = st.dataframe(get_contract_historical(user_id), hide_index=True, column_config={"reward": st.column_config.NumberColumn("Reward", format="$ %,d")})

    
with hangar_tab:
    
    col_pilot_intels, col_current_aircraft  = st.columns([1,3])
    
    with col_pilot_intels :
        
        with st.container(border=True):
            
            user_intels = get_user_intels(user_id)
            st.subheader("Pilot informations")
            
            if not user_intels.empty:
                st.markdown(f"**Username :** {user_intels['username'].iloc[0]}")
                st.markdown(f"**Wallet :** $ {user_intels['wallet'].iloc[0]:,}".replace(',', ' '))
                current_aircraft_id = user_intels.loc[0, 'current_aircraft']
                st.markdown(f"**Current aircraft :** {get_users_aircrafts_name(user_id, current_aircraft_id).loc[0,'aircraft_model']}")
                st.markdown(f"**Current location :** {user_intels['current_location'].iloc[0]}")
            else:
                st.markdown("**Username :** -")
                st.markdown("**Wallet :** $ 0")
                st.markdown("**Current aircraft :** -")
                st.markdown("**Current location :** -")




    with col_current_aircraft:

        with st.container(border=True):

            st.subheader("Current aircraft details")

            current_aircraft_details = pd.DataFrame(get_user_current_aircraft(user_id),columns=["aircraft_model", "fuel_level", "maintenance_level", "purchase_price", "purchase_date","manufacturer", "category", "engine_type", "max_speed_kts", "cruise_speed_kts", "range_nm", "avg_fuel_consumption_gal_h", "service_ceiling_ft", "max_payload_kg", "max_passengers", "edition"])

            col_1, col_2, col_3 = st.columns(3)

            with col_1:
                st.markdown(f"**Model :** {current_aircraft_details['aircraft_model'].iloc[0]}")
                st.markdown(f"**Fuel level :** {current_aircraft_details['fuel_level'].iloc[0]} %")
                st.markdown(f"**Maintenance level :** {current_aircraft_details['maintenance_level'].iloc[0]} %")
                st.markdown(f"**Range :** {current_aircraft_details['range_nm'].iloc[0]} nm")
                st.markdown(f"**Cruise speed :** {current_aircraft_details['cruise_speed_kts'].iloc[0]} kts")

            with col_2:

                st.markdown(f"**Manufacturer :** {current_aircraft_details['manufacturer'].iloc[0]}")
                st.markdown(f"**Category :** {current_aircraft_details['category'].iloc[0]}")
                st.markdown(f"**Max payload :** {current_aircraft_details['max_payload_kg'].iloc[0]} kg")
                st.markdown(f"**Max passengers :** {current_aircraft_details['max_passengers'].iloc[0]}")
                st.markdown(f"**Avg fuel consumption :** {current_aircraft_details['avg_fuel_consumption_gal_h'].iloc[0]} gal/h")

            with col_3:
                st.markdown(f"**Engine type :** {current_aircraft_details['engine_type'].iloc[0]}")
                st.markdown(f"**Max speed :** {current_aircraft_details['max_speed_kts'].iloc[0]} kts")
                st.markdown(f"**Service ceiling :** {current_aircraft_details['service_ceiling_ft'].iloc[0]} ft")
                st.markdown(f"**Purchase date :** {current_aircraft_details['purchase_date'].iloc[0]}")
                st.markdown(f"**Purchase price :** $ {current_aircraft_details['purchase_price'].iloc[0]:,}".replace(',', ' '))  


    with st.container(border=True):

        st.subheader("Hangar")
        
        st.write("List of your aircrafts in your hangar. Select one to see more details about it.")

        df_user_aircrafts = pd.DataFrame(get_users_aircrafts(user_id), columns=["id", "aircraft_model", "hangar_location", "fuel_level", "maintenance_level", "purchase_price", "purchase_date"])
        user_aircraft_selection = st.dataframe(df_user_aircrafts[["aircraft_model", "hangar_location", "fuel_level", "maintenance_level", "purchase_price", "purchase_date","id"]],
                                    hide_index=True, on_select="rerun" ,selection_mode="single-row", column_config={"purchase_price": st.column_config.NumberColumn("Purchase price", format="$ %,d")})
        
        if user_aircraft_selection.selection.rows:
            if st.button("Select this aircraft", type="primary"):
                selected_index = user_aircraft_selection.selection.rows[0]
                update_user_current_aircraft(user_id, df_user_aircrafts.iloc[selected_index]["id"])
                st.success("Current aircraft updated")
                st.rerun()

        
    
    
with shop_tab:
    
    col_list, col_info  = st.columns([1,1])
    
    with col_list :

        df_aircrafts = pd.read_csv("./data/aircraft.csv")
        
        aircraft_selection = st.dataframe(df_aircrafts[[ "name", "manufacturer","price_usd", "category", "engine_type", "max_speed_kts", "cruise_speed_kts", "range_nm", "avg_fuel_consumption_gal_h", "service_ceiling_ft", "max_payload_kg", "max_passengers", "edition" ]],
                                           hide_index=True, on_select="rerun" ,selection_mode="single-row", column_config={"price_usd": st.column_config.NumberColumn("Price", format="$ %,d")})

        
    with col_info :
        
        with st.container(border=True):
            if aircraft_selection.selection.rows:
                selected_index = aircraft_selection.selection.rows[0]
                selected_aircraft = df_aircrafts.iloc[selected_index]

                st.subheader("Aircraft details")

                col_1, col_2 = st.columns(2)

                with col_1:
                    st.markdown(f"**Name :** {selected_aircraft['name']}")
                    st.markdown(f"**Manufacturer :** {selected_aircraft['manufacturer']}")
                    st.markdown(f"**Price :** $ {selected_aircraft['price_usd']:,}".replace(',', ' '))
                    st.markdown(f"**Category :** {selected_aircraft['category']}")
                    st.markdown(f"**Engine type :** {selected_aircraft['engine_type']}")
                    st.markdown(f"**Max speed :** {selected_aircraft['max_speed_kts']} kts")
                    st.markdown(f"**Cruise speed :** {selected_aircraft['cruise_speed_kts']} kts")

                with col_2:
                    st.markdown(f"**Range :** {selected_aircraft['range_nm']} nm")
                    st.markdown(f"**Avg fuel consumption :** {selected_aircraft['avg_fuel_consumption_gal_h']} gal/h")
                    st.markdown(f"**Service ceiling :** {selected_aircraft['service_ceiling_ft']} ft")
                    st.markdown(f"**Max payload :** {selected_aircraft['max_payload_kg']} kg")
                    st.markdown(f"**Max passengers :** {selected_aircraft['max_passengers']}")
                    st.markdown(f"**Edition :** {selected_aircraft['edition']}")

                

                @st.dialog("Confirm Purchase",width="medium")
                def confirm_buy():
                    st.info(f"You are about to purchase the aircraft for **$ {selected_aircraft['price_usd']:,}**".replace(',', ' '), icon="ℹ️")

                    select_aircraft_location = st.text_input("Enter OACI code of the airport where you want to park your new aircraft :", placeholder=f"current location : {get_user_location(user_id)[0][0]}")
   
                    col_1, col_2 = st.columns(2)
                    with col_1:
                        if st.button("Confirm", type="primary",width="stretch"):
                            if pd.DataFrame(get_user_intels(user_id))[1].iloc[0] < selected_aircraft['price_usd']:
                                st.warning("You don't have enough money to purchase this aircraft.", width="stretch")
                            else:
                                if select_aircraft_location == '':
                                    st.warning("Please enter a location for your new aircraft.", width="stretch")

                                elif check_airport_location(select_aircraft_location) is False:
                                    st.warning("The entered airport code is not valid.", width="stretch")
                                else:
                                    add_user_aircraft(user_id, select_aircraft_location, selected_aircraft)
                                    expense_from_wallet(user_id, selected_aircraft['price_usd'])
                                    st.success("Aircraft purchased!", width="stretch")
                                    time.sleep(2)
                                    st.toast("A new aircraft has been added to your hangar !", icon="✈️")
                                    st.rerun()

                                
                    with col_2:
                        if st.button("Decline", type="secondary",width="stretch"):
                            st.rerun()
                    

                        

                # Boutons pour compléter le contrat
                if st.button("Buy for $ " + f"{selected_aircraft['price_usd']:,}".replace(',', ' '),type="primary", width="stretch"):
                    confirm_buy()

            else:
                st.write("ⓘ  Select an aircraft in the table.")


with bank_tab:
    st.write("Bank")