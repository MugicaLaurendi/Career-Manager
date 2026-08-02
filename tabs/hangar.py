import pandas as pd
import streamlit as st

from scripts.database_requests import (
    get_user_intels,
    get_users_aircrafts_name,
    get_user_current_aircraft,
    get_users_aircrafts,
    update_user_current_aircraft,
)


def render(user_id):

    col_pilot_intels, col_current_aircraft = st.columns([1, 3])

    with col_pilot_intels:

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

            current_aircraft_details = pd.DataFrame(get_user_current_aircraft(user_id), columns=["aircraft_model", "fuel_level", "maintenance_level", "purchase_price", "purchase_date", "manufacturer", "category", "engine_type", "max_speed_kts", "cruise_speed_kts", "range_nm", "avg_fuel_consumption_gal_h", "service_ceiling_ft", "max_payload_kg", "max_passengers"])

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
        user_aircraft_selection = st.dataframe(df_user_aircrafts[["aircraft_model", "hangar_location", "fuel_level", "maintenance_level", "purchase_price", "purchase_date", "id"]],
                                                hide_index=True, on_select="rerun", selection_mode="single-row", column_config={"purchase_price": st.column_config.NumberColumn("Purchase price", format="$ %,d")})

        if user_aircraft_selection.selection.rows:
            if st.button("Select this aircraft", type="primary"):
                selected_index = user_aircraft_selection.selection.rows[0]
                update_user_current_aircraft(user_id, df_user_aircrafts.iloc[selected_index]["id"])
                st.success("Current aircraft updated")
                st.rerun()
