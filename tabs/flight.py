import time

import folium
import streamlit as st
from streamlit_folium import st_folium

from scripts.database_requests import (
    get_user_location,
    get_airport_location,
    update_user_location,
    get_contract_accepted,
    add_contract_historical,
    income_to_wallet,
    drop_contract_accepted,
    get_contract_historical,
)


def render(user_id, airport_origin, center_lat, center_lon):

    col_free_flight, col_contracts = st.columns([1, 3])

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

            if st.session_state.dest_ff_lat != 0 and st.session_state.dest_ff_lat != 0:

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
            airport_destination_ff = st.text_input("Select a destination (OACI) :", key='free_flight_input')
            if st.button("Search destination"):
                dest_ff_coo = get_airport_location(airport_destination_ff)
                if dest_ff_coo == []:
                    st.warning("No destination selected")
                else:
                    st.session_state.dest_ff_lat = dest_ff_coo[0]
                    st.session_state.dest_ff_lon = dest_ff_coo[1]
                    st.rerun()

            if st.button(f"Flight to destination ", type="primary", width="stretch"):
                if st.session_state.dest_ff_lat == 0 and st.session_state.dest_ff_lon == 0:
                    st.warning("No destination selected")
                elif airport_destination_ff != '':
                    update_user_location(user_id, airport_destination_ff)
                    st.success(f"You have moved to {airport_destination_ff}")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.warning("No destination selected")

    with col_contracts:

        with st.container(border=True):

            st.session_state.contract = get_contract_accepted(user_id)
            contract = st.session_state.contract

            if contract is not None and not contract.empty:

                col_contract_intels, col_contract_map = st.columns([1, 2])

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

                    @st.dialog("Confirm that the contract is completed", width="medium")
                    def confirm_complete():
                        st.info(f"You are about to complete the contract", icon="ℹ️")
                        col_1, col_2 = st.columns(2)
                        with col_1:
                            if st.button("Confirm", type="primary", width="stretch"):
                                if get_contract_accepted(user_id).empty == False:
                                    add_contract_historical(st.session_state.contract, user_id, "completed")
                                    income_to_wallet(user_id, st.session_state.contract.loc[0, 'reward'])
                                    update_user_location(user_id, st.session_state.contract.loc[0, 'arrival_airport'])
                                    st.success("Contract completed", width="stretch")
                                    time.sleep(2)
                                    st.session_state.contract = 0
                                    drop_contract_accepted(user_id)
                                    st.rerun()
                        with col_2:
                            if st.button("Decline", type="secondary", width="stretch"):
                                st.rerun()

                    @st.dialog("Confirm the abort of the contract", width="medium")
                    def confirm_abort():
                        st.warning(f"You are about to abort the contract", icon="⚠️")
                        col_1, col_2 = st.columns(2)
                        with col_1:
                            if st.button("Confirm", type="primary", width="stretch"):
                                add_contract_historical(st.session_state.contract, user_id, "aborted")
                                st.warning("Contract aborted")
                                time.sleep(2)
                                st.session_state.contract = 0
                                drop_contract_accepted(user_id)
                                st.rerun()
                        with col_2:
                            if st.button("Decline", type="secondary", width="stretch"):
                                st.rerun()

                    # Boutons pour compléter le contrat
                    if left.button("Completed", type="primary", width="stretch"):
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
                            location=[contract.loc[0, 'latitude'], contract.loc[0, 'longitude']],
                            tooltip=f"OACI: {contract['arrival_airport'].iloc[0]}</br> Contract ID: {contract.iloc[0, 0]}</br> Distance: {contract['distance_nm'].iloc[0]} nm</br> Reward: ${contract['reward'].iloc[0]}",
                            icon=folium.Icon(color="blue", icon="book")
                        ).add_to(m)

                        # Ajout de la ligne reliant les deux points
                        folium.PolyLine(
                            locations=[(center_lat, center_lon), (contract.loc[0, 'latitude'], contract.loc[0, 'longitude'])],
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
