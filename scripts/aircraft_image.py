import base64
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
AIRCRAFT_IMAGES_DIR = DATA_DIR / "images" / "aircrafts"
AIRCRAFT_CSV_PATH = DATA_DIR / "aircraft.csv"


def get_aircraft_image_path(aircraft_model):

    df_aircrafts = pd.read_csv(AIRCRAFT_CSV_PATH, usecols=["id", "name"])
    match = df_aircrafts.loc[df_aircrafts["name"] == aircraft_model, "id"]
    if match.empty:
        return None

    # Les images ont des extensions variables (jpg, webp, avif...)
    for image_path in AIRCRAFT_IMAGES_DIR.glob(f"{int(match.iloc[0])}.*"):
        return str(image_path)
    return None


@st.cache_data(show_spinner=False)
def get_aircraft_thumbnail(aircraft_id, size=(160, 100)):
    """Miniature de l'avion en data URI (st.dataframe n'accepte pas les chemins locaux)."""

    for image_path in AIRCRAFT_IMAGES_DIR.glob(f"{int(aircraft_id)}.*"):
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            image.thumbnail(size)
            buffer = BytesIO()
            image.save(buffer, format="JPEG", quality=80)
        return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()
    return None
