from datetime import datetime

import streamlit as st

from scripts.database_requests import get_all_users, create_user, delete_user
from scripts.profile_image import save_profile_image, delete_profile_image


@st.dialog("Delete profile")
def confirm_delete(user_id, username):
    st.warning(f"You are about to permanently delete **{username}**: wallet, aircrafts and contract history will be lost.", icon="⚠️")

    col_1, col_2 = st.columns(2)
    with col_1:
        if st.button("Delete", type="primary", width="stretch"):
            delete_user(user_id)
            delete_profile_image(user_id)
            st.rerun()
    with col_2:
        if st.button("Cancel", width="stretch"):
            st.rerun()


def render():

    with st.container(border=True):

        st.subheader("Select your profile")

        existing_users = get_all_users()

        if not existing_users.empty:
            for _, user in existing_users.iterrows():
                col_login, col_delete = st.columns([5, 1])
                with col_login:
                    if st.button(f"**{user['username']}**", key=f"login_{user['id']}", width="stretch", type="primary"):
                        st.session_state.user_id = int(user['id'])
                        print(f"{datetime.now()} User {user['username']} (ID: {user['id']}) logged in.")
                        st.rerun()
                with col_delete:
                    if st.button("", key=f"delete_{user['id']}", icon=":material/delete:", help=f"Delete {user['username']}", width="stretch"):
                        confirm_delete(int(user['id']), user['username'])
        else:
            st.write("No profile yet, create one below to get started.")



        # st.button n'est True que sur le rerun qui suit le clic : on mémorise l'ouverture
        # du formulaire, sinon il disparaît dès que l'on clique sur "Create profile".
        if st.button("Create new profile", width="stretch"):
            st.session_state.show_create_profile = True

        if st.session_state.get("show_create_profile"):

            with st.form("create_profile_form"):
                new_username = st.text_input("Username")
                new_profile_picture = st.file_uploader(
                    "Profile picture (optional, drag and drop)",
                    type=["png", "jpg", "jpeg"],
                )
                submitted = st.form_submit_button("Create profile", type="primary")

                if submitted:
                    if not new_username.strip():
                        st.warning("Please enter a username.")
                    else:
                        new_user_id = create_user(new_username)
                        if new_user_id is None:
                            st.warning("This username is already taken.")
                        else:
                            if new_profile_picture is not None:
                                save_profile_image(new_user_id, new_profile_picture)
                            st.session_state.user_id = new_user_id
                            st.rerun()
