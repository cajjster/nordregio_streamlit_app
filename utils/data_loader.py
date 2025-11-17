# utils/data_loader.py
import pandas as pd
import geopandas as gpd
import json
import os
import streamlit as st

# --- Base data path ---
BASE_PATH = "/Users/axelcajselius/Documents/GitHub/nordregio_streamlit_app/data"


# --- Load CSV salaries ---
@st.cache_data
def load_salaries(filename: str = "avg_salaries_se.csv") -> pd.DataFrame:
    """
    Load salary CSV into a pandas DataFrame.
    Safe to cache since it's a simple DataFrame.
    """
    path = os.path.join(BASE_PATH, filename)
    df = pd.read_csv(path)
    return df


# --- Load GeoPackage or GeoJSON as GeoDataFrame ---
def load_geodata(filename: str = "nordics.gpkg") -> gpd.GeoDataFrame:
    """
    Load a geospatial file (GeoPackage or GeoJSON) as a GeoDataFrame.
    NOT cached — GeoDataFrames are unhashable in Streamlit.
    """
    path = os.path.join(BASE_PATH, filename)
    gdf = gpd.read_file(path)
    geojson = json.loads(gdf.to_json())
    return gdf, geojson


# --- Merge salaries with GeoDataFrame ---
def merge_salaries_geo(gdf: gpd.GeoDataFrame, df: pd.DataFrame,
                       key_gdf: str = "Mun Code", key_df: str = "mun") -> gpd.GeoDataFrame:
    """
    Merge salaries DataFrame with GeoDataFrame.
    NOT cached — uses a GeoDataFrame argument (unhashable).
    """
    merged = gdf.merge(df, left_on=key_gdf, right_on=key_df, how="inner")
    return merged


df = load_salaries()
print(df.head())
gdf, geojson = load_geodata("nordics.gpkg")  # or .geojson
print(gdf.head)
gdf_merged = merge_salaries_geo(gdf, df)
print(gdf_merged.head())
