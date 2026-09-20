import streamlit as st
from datetime import datetime

from scripts.database_requests import get_user_intels, get_users_aircrafts_name
from scripts.profile_image import get_profile_image_path, change_profil_picture


def render(user_id):

    user_intels = get_user_intels(user_id)

    if st.button("Logout", width="stretch"):
        st.session_state.clear()
        print(f"{datetime.now()} User {user_intels['username'].iloc[0]} logged out.")
        st.rerun()

    with st.container(border=True):

        st.image(get_profile_image_path(user_id))

        if st.button("Change picture", icon=":material/photo_camera:", width="stretch"):
            change_profil_picture(user_id)

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
