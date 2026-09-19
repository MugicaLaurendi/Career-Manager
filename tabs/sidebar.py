import streamlit as st

from scripts.database_requests import get_user_intels, get_users_aircrafts_name


def render(user_id):

    with st.container(border=True):

        st.image("data/images/pilote_placeholder.png")

        user_intels = get_user_intels(user_id)
        st.subheader("Pilot informations")

        if not user_intels.empty:
            st.markdown(f"**Username :** {user_intels['username'].iloc[0]}")
            st.markdown(f"**Wallet :** $ {user_intels['wallet'].iloc[0]:,}".replace(',', ' '))
            current_aircraft_id = int(user_intels.loc[0, 'current_aircraft'])
            st.markdown(f"**Current aircraft :** {get_users_aircrafts_name(user_id, current_aircraft_id).loc[0,'aircraft_model']}")
            st.markdown(f"**Current location :** {user_intels['current_location'].iloc[0]}")
        else:
            st.markdown("**Username :** -")
            st.markdown("**Wallet :** $ 0")
            st.markdown("**Current aircraft :** -")
            st.markdown("**Current location :** -")
