import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_salaries, load_geodata, merge_salaries_geo
from modules.plots import render_choropleth_tab, render_gender_tab, render_top_bottom_tab, render_distribution_tab, render_municipality_tab, render_change_tab, render_summary_tab

# --- Streamlit page ---
st.set_page_config(page_title="Salary Sweden", layout="wide")
col_logo, col_title = st.columns([1, 8])

with col_logo:
    st.image("assets/Nordregio-Logotype-dark-blue.png", width=250)

with col_title:
    st.title("AVERAGE SALARIES IN SWEDEN")

# --- Load data ---
df = load_salaries()
gdf, geojson = load_geodata("nordics.gpkg")  # or .geojson
gdf_merged = merge_salaries_geo(gdf, df)

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Choropleth Map", "Gender Pay Gap", "10 Richest and Poorest Municipalities", "Salary Distribution", "Salary by Municipality", "Salary Change % ", "Summary Stats"])

with tab1:
    render_choropleth_tab(gdf_merged, geojson)

with tab2:
    render_gender_tab(df)
  
with tab3:
    render_top_bottom_tab(df)

with tab4:
    render_distribution_tab(df)

with tab5:
    render_municipality_tab(df)

with tab6:
    render_change_tab(df)

with tab7:
    render_summary_tab(df)


