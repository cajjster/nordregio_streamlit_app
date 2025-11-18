# utils/data_loader.py
import os
import json
import pandas as pd
import streamlit as st

# --- Base data path ---
BASE_PATH = "/Users/axelcajselius/Documents/GitHub/nordregio_streamlit_app/data"


# --- Load salary CSV ---
@st.cache_data
def load_salaries(filename: str = "avg_salaries_se.csv") -> pd.DataFrame:
    """
    Load salary CSV into a pandas DataFrame.
    Safe to cache since it's a simple DataFrame.
    """
    path = os.path.join(BASE_PATH, filename)
    df = pd.read_csv(path)

    # Ensure mun column is string (important for matching)
    df["mun"] = df["mun"].astype(str)

    return df


# --- Load GeoJSON without GeoPandas ---
@st.cache_data
def load_geojson(filename: str = "nordics.geojson"):
    """
    Load a GeoJSON file using json.load.
    Returns the raw GeoJSON dict.
    """
    path = os.path.join(BASE_PATH, filename)
    with open(path, "r") as f:
        geojson = json.load(f)

    return geojson

