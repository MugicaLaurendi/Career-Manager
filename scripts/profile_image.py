from pathlib import Path

import streamlit as st
from PIL import Image


PROFILE_IMAGES_DIR = Path(__file__).resolve().parent.parent / "data" / "images" / "profiles"
PLACEHOLDER_IMAGE_PATH = Path(__file__).resolve().parent.parent / "data" / "images" / "profil_placeholder.png"


def save_profile_image(user_id, uploaded_file):

    PROFILE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    image_path = PROFILE_IMAGES_DIR / f"{user_id}.png"

    image = Image.open(uploaded_file)
    image.convert("RGBA").save(image_path, format="PNG")

    return image_path

@st.dialog("Change profile picture")
def change_profil_picture(user_id):

    new_picture = st.file_uploader(
        "Drag and drop your new profile picture",
        type=["png", "jpg", "jpeg"],
    )

    if st.button("Save", type="primary", width="stretch", disabled=new_picture is None):
        save_profile_image(user_id, new_picture)
        st.rerun()

def delete_profile_image(user_id):

    image_path = PROFILE_IMAGES_DIR / f"{user_id}.png"
    image_path.unlink(missing_ok=True)

def get_profile_image_path(user_id):

    image_path = PROFILE_IMAGES_DIR / f"{user_id}.png"
    if image_path.exists():
        return str(image_path)
    return str(PLACEHOLDER_IMAGE_PATH)
