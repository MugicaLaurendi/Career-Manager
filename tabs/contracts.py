import time
from datetime import datetime

import folium
import streamlit as st
from streamlit_folium import st_folium

from scripts.search_contract import search_contract, search_airport, CONTRACT_TYPES_TUPLE
from scripts.database_requests import get_user_location, get_contract_accepted, drop_contract_accepted, add_contract_accepted


def render(user_id):
    col_sidebar, col_content = st.columns([1, 3])

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

        dist_min = st.number_input("Distance min", value=50, step=100)
        dist_max = st.number_input("Distance max", value=100, step=100)

        if st.button("Search contracts", type="primary", width="stretch"):
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

            for index, contract in df_contracts.iterrows():

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

        col1, col2 = st.columns([2, 1])

        # ----- TABLEAU DES CONTRATS -----

        with col1:

            contract_selection = st.dataframe(df_contracts[["contract_category", "departure_airport", "arrival_airport", "distance_nm", "reward"]], hide_index=False, on_select="rerun", selection_mode="single-row", column_config={"reward": st.column_config.NumberColumn("Reward", format="$ %,d")})

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

                    with st.container(border=True, width="content", gap="xxlarge"):

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

                    @st.dialog("Are you sure you want to accept this contract?", width="medium")
                    def confirm_accept():
                        st.write(f"You are about to accept the contract to {selected_row['arrival_airport']} with a reward of $ {selected_row['reward']:,}".replace(',', ' '))
                        col_1, col_2 = st.columns(2)
                        with col_1:
                            if st.button("Confirm", type="primary", width="stretch"):
                                if get_contract_accepted(user_id).empty == False:
                                    st.warning("You already have an accepted contract. Please complete or abort it before accepting a new one.", icon="⚠️", width="stretch")
                                else:
                                    drop_contract_accepted(user_id)
                                    add_contract_accepted(selected_row, user_id)
                                    st.success("Contract accepted", width="stretch")
                                    time.sleep(2)
                                    st.rerun()
                        with col_2:
                            if st.button("Decline", type="secondary", width="stretch"):
                                st.rerun()

                    if st.button("Accept contract", type="primary", width="stretch"):
                        confirm_accept()

                else:
                    st.write("ⓘ  Sélectionnez un contrat dans le tableau.")

    return airport_origin, center_lat, center_lon
