import streamlit as st
import plotly.express as px



# ============================================================
#   TAB 1 — CHOROPLETH MAP
# ============================================================
def render_choropleth_tab(df, geojson):
    """
    Renders the choropleth salary map tab.
    Uses df + geojson only (no GeoPandas).
    """

    st.title("Swedish Municipal Salary Map (2007-2024) 🇸🇪")

    # ---- Controls ----
    years = sorted(df["year"].unique())
    default_year = max(years)

    col1, col2 = st.columns([3, 1])

    with col1:
        year_selected = st.slider(
            "Select Year",
            min_value=min(years),
            max_value=max(years),
            value=default_year,
            step=1,
            key="choropleth_year"
        )

    with col2:
        variable = st.selectbox(
            "Select Salary Type",
            options=["total", "men", "women"],
            index=0,
            key="choropleth_variable"
        )

    # ---- Filter ----
    df_year = df[df["year"] == year_selected].copy()

    # ---- Plot ----
    fig = px.choropleth_mapbox(
        df_year,
        geojson=geojson,
        locations="mun",                     # KEY IN YOUR DF
        featureidkey="properties.Mun Code",  # MATCHES GEOJSON
        color=variable,
        hover_name="municipality",
        hover_data={
            "total": True,
            "men": True,
            "women": True,
            "year": True,
            "mun": True,
        },
        mapbox_style="carto-positron",
        zoom=3.8,
        center={"lat": 62.0, "lon": 15.0},
        opacity=0.75,
        color_continuous_scale="Viridis",
    )

    fig.update_layout(
        height=700,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    # ---- Render ----
    st.subheader(f"Salaries shown for: **{variable.capitalize()}** in **{year_selected}**")
    st.plotly_chart(fig, use_container_width=True)



# ============================================================
#   TAB 2 — GENDER PAY GAP & MEN vs WOMEN SCATTER
# ============================================================
def render_gender_tab(df):
    """
    Renders the gender pay gap tab.
    Handles:
    - Sweden time-series line chart
    - Year selector
    - Scatterplot men vs women
    - Rendering inside Streamlit
    """

    st.header("Salary Evolution Over Time (Sweden)")

    # ---- Sweden-only ----
    df_sweden = df[df['mun'] == "SE00"]

    # Long format for line chart
    df_long = df_sweden.melt(
        id_vars="year",
        value_vars=["total", "men", "women"],
        var_name="Salary Type",
        value_name="Salary"
    )

    # ---- Line chart ----
    fig1 = px.line(
        df_long,
        x="year",
        y="Salary",
        color="Salary Type",
        markers=True,
        title="Average Salaries in Sweden Over Time"
    )

    st.plotly_chart(fig1, use_container_width=True)

    # ---- Scatter plot: men vs women ----
    col1, col2 = st.columns(2)

    with col1:
        st.header("Salaries for Men vs Women Across Municipalities")

        years = sorted(df['year'].unique())
        selected_year = st.select_slider(
            "Select Year",
            options=years,
            value=years[-1],  # default latest year
            key="gender_scatter_year"
        )

        # Filter & exclude Sweden aggregate
        df_year = df[(df['year'] == selected_year) & (df['mun'] != "SE00")]

        fig2 = px.scatter(
            df_year,
            x='men',
            y='women',
            hover_name='mun',
            labels={'men': 'Men Average Salary', 'women': 'Women Average Salary'},
            title=f"Men vs Women Salaries in {selected_year}"
        )

        # Reference line (x=y)
        fig2.add_shape(
            type="line",
            x0=df_year['men'].min(),
            y0=df_year['men'].min(),
            x1=df_year['men'].max(),
            y1=df_year['men'].max(),
            line=dict(color="red", dash="dash"),
        )

        fig2.update_layout(
            xaxis_title="Men Average Salary",
            yaxis_title="Women Average Salary",
            height=600
        )

        st.plotly_chart(fig2, use_container_width=True)

def render_top_bottom_tab(df):
    """
    Renders the Top 10 / Bottom 10 municipalities tab.
    Handles:
    - Year selector
    - Filtering out Sweden (SE00)
    - Two bar charts side-by-side
    """

    st.header("Top/Bottom 10 Municipalities by Average Salary")

    years = sorted(df['year'].unique())
    selected_year = st.select_slider("Select Year", options=years, value=years[-1], key="top_bottom_year")

    # Filter data
    df_year = df[df['year'] == selected_year]
    df_mun = df_year[df_year['mun'] != "SE00"]

    # Common y-axis limits for comparable bars
    min_total = 20000
    max_total = 40000

    col1, col2 = st.columns(2)

    # --- Top 10 ---
    with col1:
        top10 = df_mun.nlargest(10, 'total')
        fig_top = px.bar(
            top10,
            x='municipality',
            y='total',
            labels={'municipality': 'Municipality', 'total': 'Average Salary (SEK)'},
            title=f"Top 10 Municipalities – {selected_year}"
        )
        fig_top.update_yaxes(range=[min_total, max_total], tickformat=",.0f")
        fig_top.update_xaxes(tickangle=45)
        st.plotly_chart(fig_top, use_container_width=True)

    # --- Bottom 10 ---
    with col2:
        bottom10 = df_mun.nsmallest(10, 'total')
        fig_bottom = px.bar(
            bottom10,
            x='municipality',
            y='total',
            labels={'municipality': 'Municipality', 'total': 'Average Salary (SEK)'},
            title=f"Bottom 10 Municipalities – {selected_year}"
        )
        fig_bottom.update_yaxes(range=[min_total, max_total], tickformat=",.0f")
        fig_bottom.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bottom, use_container_width=True)

import plotly.graph_objects as go

def render_distribution_tab(df):
    """
    Renders the salary distribution histogram.
    Handles:
    - Year selector
    - Filtering out Sweden
    - Overlaid histograms (total/men/women)
    """

    st.header("Salary Distribution Across Municipalities")

    years = sorted(df['year'].unique())
    selected_year = st.select_slider("Select Year", options=years, value=years[-1], key="dist_year")

    # Filter out Sweden (SE00)
    df_year = df[(df['year'] == selected_year) & (df['mun'] != "SE00")]

    fig = go.Figure()

    for col, color in zip(["total", "men", "women"], ["blue", "green", "red"]):
        fig.add_trace(go.Histogram(
            x=df_year[col],
            name=col.capitalize(),
            marker_color=color,
            opacity=0.75
        ))

    fig.update_layout(
        barmode="overlay",
        title=f"Distribution of Salaries – {selected_year}",
        xaxis_title="Average Salary (SEK)",
        yaxis_title="Count",
        legend_title="Category"
    )

    st.plotly_chart(fig, use_container_width=True)

def render_municipality_tab(df):
    """
    Renders the municipality comparison over time tab.
    Handles:
    - Multi-select for municipalities
    - Sweden included by default
    - Line chart of total salaries
    """

    st.header("Average Salaries Over Time by Municipality")

    # Sweden's name
    sweden_name = df.loc[df['mun'] == "SE00", "municipality"].iloc[0]

    all_muns = sorted(df['municipality'].unique())

    selected_muns = st.multiselect(
        "Select Municipalities to Compare",
        options=all_muns,
        default=[sweden_name],
        key="mun_compare_select"
    )

    # Filter for selected municipalities
    plot_df = df[df['municipality'].isin(selected_muns)]

    fig = px.line(
        plot_df,
        x='year',
        y='total',
        color='municipality',
        labels={'year': 'Year', 'total': 'Average Salary (SEK)'},
        title="Average Salaries Over Time"
    )

    st.plotly_chart(fig, use_container_width=True)

def render_change_tab(df):
    """
    Renders the percentage salary change tab.
    Handles:
    - Multi-select
    - Percentage change from base year
    - Line chart
    """

    st.header("Average Salaries Over Time by Municipality (Percentage Change)")

    sweden_name = df.loc[df['mun'] == "SE00", "municipality"].iloc[0]
    all_muns = sorted(df['municipality'].unique())

    selected_muns = st.multiselect(
        "Select Municipalities to Compare",
        options=all_muns,
        default=[sweden_name],
        key="pct_change_mun_select"
    )

    # Compute % change
    plot_df = df[df['municipality'].isin(selected_muns)].copy()
    plot_df['pct_increase'] = plot_df.groupby('municipality')['total'].transform(
        lambda x: (x - x.iloc[0]) / x.iloc[0] * 100
    )

    fig = px.line(
        plot_df,
        x='year',
        y='pct_increase',
        color='municipality',
        labels={'year': 'Year', 'pct_increase': 'Salary Increase (%)'},
        title="Salary Percentage Increase Over Time"
    )

    st.plotly_chart(fig, use_container_width=True)

def render_summary_tab(df):
    """
    Renders the summary stats tab.
    Handles:
    - 2024 mean salaries
    - Highest % increase since base year
    - Lowest % increase since base year
    """

    st.header("Summary Stats")

    col1, col2, col3 = st.columns(3)

    # ---- Column 1: Average salaries (2024) ----
    with col1:
        df_2024 = df[df['year'] == 2024]

        avg_total = df_2024['total'].mean()
        avg_men = df_2024['men'].mean()
        avg_women = df_2024['women'].mean()

        st.header("Average Salaries in Sweden (2024)")
        st.metric("Total", f"{avg_total:,.0f} SEK")
        st.metric("Men", f"{avg_men:,.0f} SEK")
        st.metric("Women", f"{avg_women:,.0f} SEK")

    # ---- Prep shared data for col2 + col3 ----
    base_year = df['year'].min()
    latest_year = df['year'].max()

    df_pct = df.copy()
    for col in ['total', 'men', 'women']:
        df_pct[col + '_pct'] = df_pct.groupby('mun')[col].transform(
            lambda x: (x - x.iloc[0]) / x.iloc[0] * 100
        )

    df_latest = df_pct[df_pct['year'] == latest_year]

    # ---- Column 2: Highest increases ----
    with col2:
        st.header(f"Highest Salary Increase ({base_year} → {latest_year})")

        top_total = df_latest.loc[df_latest['total_pct'].idxmax()]
        top_men = df_latest.loc[df_latest['men_pct'].idxmax()]
        top_women = df_latest.loc[df_latest['women_pct'].idxmax()]

        st.metric(label=f"Total — {top_total['municipality']}", value=f"{top_total['total_pct']:.1f}%")
        st.metric(label=f"Men — {top_men['municipality']}", value=f"{top_men['men_pct']:.1f}%")
        st.metric(label=f"Women — {top_women['municipality']}", value=f"{top_women['women_pct']:.1f}%")

    # ---- Column 3: Lowest increases ----
    with col3:
        st.header(f"Lowest Salary Increase ({base_year} → {latest_year})")

        low_total = df_latest.loc[df_latest['total_pct'].idxmin()]
        low_men = df_latest.loc[df_latest['men_pct'].idxmin()]
        low_women = df_latest.loc[df_latest['women_pct'].idxmin()]

        st.metric(label=f"Total — {low_total['municipality']}", value=f"{low_total['total_pct']:.1f}%")
        st.metric(label=f"Men — {low_men['municipality']}", value=f"{low_men['men_pct']:.1f}%")
        st.metric(label=f"Women — {low_women['municipality']}", value=f"{low_women['women_pct']:.1f}%")
