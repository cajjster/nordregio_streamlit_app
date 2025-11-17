import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_salaries, load_geodata, merge_salaries_geo

# --- Streamlit page ---
st.set_page_config(page_title="Salary Sweden", layout="wide")
st.title("Average Salaries in Sweden")

# --- Load data ---
df = load_salaries()
gdf, geojson = load_geodata("nordics.gpkg")  # or .geojson
gdf_merged = merge_salaries_geo(gdf, df)

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Overview", "Men vs. Women", "Top 10", "Salary Distribution", "Salary by Municipality", "Salary Change % ", "head"])

with tab1:
    st.header("Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        # --- Filter for 2024 ---
        df_2024 = df[df['year'] == 2024]

        # --- Compute average salaries ---
        avg_total = df_2024['total'].mean()
        avg_men = df_2024['men'].mean()
        avg_women = df_2024['women'].mean()

        # --- Display ---
        st.header("Average Salaries in Sweden (2024)")
        st.metric("Total", f"{avg_total:,.0f} SEK")
        st.metric("Men", f"{avg_men:,.0f} SEK")
        st.metric("Women", f"{avg_women:,.0f} SEK")

    with col2:
        
        base_year = df['year'].min()

        # --- Compute percentage increase from base year for each municipality ---
        df_pct = df.copy()
        for col in ['total', 'men', 'women']:
            df_pct[col + '_pct'] = df_pct.groupby('mun')[col].transform(
                lambda x: (x - x.iloc[0]) / x.iloc[0] * 100
            )

        # --- Filter for last year (most recent) ---
        latest_year = df['year'].max()
        df_latest = df_pct[df_pct['year'] == latest_year]

        # --- Find municipalities with highest percentage increase ---
        top_total = df_latest.loc[df_latest['total_pct'].idxmax()]
        top_men = df_latest.loc[df_latest['men_pct'].idxmax()]
        top_women = df_latest.loc[df_latest['women_pct'].idxmax()]

        # --- Display results ---
        st.header(f"Highest Salary Increase from {base_year} to {latest_year}")


        st.metric(label=f"Total — {top_total['municipality']}", value=f"{top_total['total_pct']:.1f}%")
        st.metric(label=f"Men — {top_men['municipality']}", value=f"{top_men['men_pct']:.1f}%")
        st.metric(label=f"Women — {top_women['municipality']}", value=f"{top_women['women_pct']:.1f}%")

    with col3:
        base_year = df['year'].min()

        # --- Compute percentage increase from base year for each municipality ---
        df_pct = df.copy()
        for col in ['total', 'men', 'women']:
            df_pct[col + '_pct'] = df_pct.groupby('mun')[col].transform(
                lambda x: (x - x.iloc[0]) / x.iloc[0] * 100
            )

        # --- Filter for last year (most recent) ---
        latest_year = df['year'].max()
        df_latest = df_pct[df_pct['year'] == latest_year]

        # --- Find municipalities with lowest percentage increase ---
        low_total = df_latest.loc[df_latest['total_pct'].idxmin()]
        low_men = df_latest.loc[df_latest['men_pct'].idxmin()]
        low_women = df_latest.loc[df_latest['women_pct'].idxmin()]

        # --- Display results ---
        st.header(f"Lowest Salary Increase from {base_year} to {latest_year}")

        st.metric(label=f"Total — {low_total['municipality']}", value=f"{low_total['total_pct']:.1f}%")
        st.metric(label=f"Men — {low_men['municipality']}", value=f"{low_men['men_pct']:.1f}%")
        st.metric(label=f"Women — {low_women['municipality']}", value=f"{low_women['women_pct']:.1f}%")

with tab2:
    st.header("Salary Evolution Over Time (Sweden)")

    #  Filter for Sweden only (SE00)
    df_se = df[df['mun'] == "SE00"]

    # Melt to long format for Plotly Express (optional, makes lines automatic)
    df_long = df_se.melt(id_vars="year", value_vars=["total", "men", "women"],
                        var_name="Salary Type", value_name="Salary")

    # Create line plot
    fig = px.line(df_long, x="year", y="Salary", color="Salary Type",
                markers=True, title="Average Salaries in Sweden Over Time")

    # Show plot
    st.plotly_chart(fig, use_container_width=True)

    df_sweden = df[df['mun'] == "SE00"]

    col1, col2 = st.columns(2)

    with col1:

        # Scatter/line plot comparing men vs women over time

        st.header("Salaries for Men vs Women Across Municipalities")

        # --- Select year ---
        years = sorted(df['year'].unique())
        selected_year = st.select_slider("Select Year", options=years, value=2024, key="scatter_year_slider")

        # --- Filter data ---
        df_year = df[(df['year'] == selected_year) & (df['mun'] != "SE00")]  # exclude total Sweden

        # --- Scatterplot ---
        fig = px.scatter(
            df_year,
            x='men',
            y='women',
            hover_name='mun',   # show municipality on hover
            labels={'men': 'Men Average Salary', 'women': 'Women Average Salary'},
            title=f"Men vs Women Salaries in {selected_year}"
        )

        # Add a 45-degree reference line (men = women) for comparison
        fig.add_shape(
            type="line",
            x0=df_year['men'].min(),
            y0=df_year['men'].min(),
            x1=df_year['men'].max(),
            y1=df_year['men'].max(),
            line=dict(color="red", dash="dash"),
            name="Men = Women"
        )

        fig.update_layout(
            xaxis_title="Men Average Salary",
            yaxis_title="Women Average Salary",
            legend_title="",
            width=800,
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)
  


with tab3:
    st.header("Top/Bottom 10 Municipalities by Average Salary")

    # --- Year selector ---
    years = sorted(df['year'].unique())
    selected_year = st.select_slider("Select Year", options=years, value=2024)

    # --- Filter data for selected year ---
    df_year = df[df['year'] == selected_year]
    df_mun = df_year[df_year['mun'] != "SE00"]

    # --- set min and max for y-axis ---
    min_total = 20000
    max_total = 40000

    col1, col2 = st.columns(2)

    with col1:
        top10 = df_mun.nlargest(10, 'total')
        fig_top = px.bar(
            top10,
            x='municipality',
            y='total',
            labels={'municipality': 'Municipality', 'total': 'Average Salary (SEK)'},
            title=f"Top 10 Municipalities - {selected_year}"
        )
        fig_top.update_yaxes(range=[min_total, max_total], tickformat=",.0f")
        fig_top.update_xaxes(tickangle=45)
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        bottom10 = df_mun.nsmallest(10, 'total')
        fig_bottom = px.bar(
            bottom10,
            x='municipality',
            y='total',
            labels={'municipality': 'Municipality', 'total': 'Average Salary (SEK)'},
            title=f"Bottom 10 Municipalities - {selected_year}"
        )
        fig_bottom.update_yaxes(range=[min_total, max_total], tickformat=",.0f")
        fig_bottom.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bottom, use_container_width=True)


with tab4:
    st.header("Salary Distribution Across Municipalities")   

    # --- Select year ---
    years = sorted(df['year'].unique())
    selected_year = st.select_slider("Select Year", options=years, value=2024, key="dist_year")

    # --- Filter data ---
    df_year = df[(df['year'] == selected_year) & (df['mun'] != "SE00")]

    # --- Create interactive histogram ---
    fig = go.Figure()

    # Add a trace for each salary type
    for col, color in zip(["total", "men", "women"], ["blue", "green", "red"]):
        fig.add_trace(go.Histogram(
            x=df_year[col],
            name=col.capitalize(),
            marker_color=color,
            opacity=0.75  # slight transparency to see overlaps
        ))

    fig.update_layout(
        barmode='overlay',  # overlay so bars stack visually
        title=f"Distribution of Salaries - {selected_year}",
        xaxis_title="Average Salary",
        yaxis_title="Count",
        legend_title="Category"
    )

    st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.header("Average Salaries Over Time by Municipality")

# Find the municipality name for Sweden
    sweden_name = df.loc[df['mun'] == "SE00", "municipality"].iloc[0]

    # --- Municipality multi-select ---
    all_muns = sorted(df['municipality'].unique())
    selected_muns = st.multiselect(
        "Select Municipalities to Compare",
        options=all_muns,
        default=[sweden_name]  # show Sweden first
    )

    # --- Filter df for selected municipalities ---
    plot_df = df[df['municipality'].isin(selected_muns)]

    # --- Plot line chart ---
    fig = px.line(
        plot_df,
        x='year',
        y='total',
        color='municipality',
        labels={'year': 'Year', 'total': 'Average Salary (SEK)'},
        title="Average Salaries Over Time"
    )

    st.plotly_chart(fig, use_container_width=True)

with tab6:
    st.header("Average Salaries Over Time by Municipality (Percentage Change)")

    # --- Find Sweden's municipality name ---
    sweden_name = df.loc[df['mun'] == "SE00", "municipality"].iloc[0]

    # --- Municipality multi-select ---
    all_muns = sorted(df['municipality'].unique())
    selected_muns = st.multiselect(
        "Select Municipalities to Compare",
        options=all_muns,
        default=[sweden_name],  # show Sweden first
        key="pct_change_mun_select"
    )

    # --- Filter df for selected municipalities ---
    plot_df = df[df['municipality'].isin(selected_muns)].copy()

    # --- Calculate percentage increase from base year for each municipality ---
    plot_df['pct_increase'] = plot_df.groupby('municipality')['total'].transform(
        lambda x: (x - x.iloc[0]) / x.iloc[0] * 100
    )

    # --- Plot line chart ---
    fig = px.line(
        plot_df,
        x='year',
        y='pct_increase',
        color='municipality',
        labels={'year': 'Year', 'pct_increase': 'Salary Increase (%)'},
        title="Salary Percentage Increase Over Time"
    )

    st.plotly_chart(fig, use_container_width=True)


with tab7:
    st.header("Inspect Data")

    st.subheader("Salaries DataFrame (df)")
    st.dataframe(df.head())

    st.subheader("GeoDataFrame (gdf)")
    st.dataframe(gdf.head())

    st.subheader("Merged GeoDataFrame (gdf_merged)")
    st.dataframe(gdf_merged.head())

    st.subheader("GeoJSON (geojson) - first 3 features")
    st.json(geojson['features'][:3])