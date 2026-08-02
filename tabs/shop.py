import time

import pandas as pd
import streamlit as st

from scripts.database_requests import (
    get_user_intels,
    get_user_location,
    check_airport_location,
    add_user_aircraft,
    expense_from_wallet,
)


def render(user_id):

    col_list, col_info = st.columns([1, 1])

    with col_list:

        df_aircrafts = pd.read_csv("./data/aircraft.csv")

        aircraft_selection = st.dataframe(df_aircrafts[["name", "manufacturer", "price_usd", "category", "engine_type", "max_speed_kts", "cruise_speed_kts", "range_nm", "avg_fuel_consumption_gal_h", "service_ceiling_ft", "max_payload_kg", "max_passengers"]],
                                           hide_index=True, on_select="rerun", selection_mode="single-row", column_config={"price_usd": st.column_config.NumberColumn("Price", format="$ %,d")})

    with col_info:

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

                @st.dialog("Confirm Purchase", width="medium")
                def confirm_buy():
                    st.info(f"You are about to purchase the aircraft for **$ {selected_aircraft['price_usd']:,}**".replace(',', ' '), icon="ℹ️")

                    select_aircraft_location = st.text_input("Enter OACI code of the airport where you want to park your new aircraft :", placeholder=f"current location : {get_user_location(user_id)[0][0]}")

                    col_1, col_2 = st.columns(2)
                    with col_1:
                        if st.button("Confirm", type="primary", width="stretch"):
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
                        if st.button("Decline", type="secondary", width="stretch"):
                            st.rerun()

                # Boutons pour compléter le contrat
                if st.button("Buy for $ " + f"{selected_aircraft['price_usd']:,}".replace(',', ' '), type="primary", width="stretch"):
                    confirm_buy()

            else:
                st.write("ⓘ  Select an aircraft in the table.")
