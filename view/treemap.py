import streamlit as st
import pandas as pd
import plotly.graph_objs as go


# -----------------------------
# Treemap builder w/ filters
# -----------------------------
@st.cache_data(show_spinner=False)
def build_treemap_figure(
    df: pd.DataFrame,
    start_year: int,
    end_year: int,
    selected_genres_tuple: tuple,
) -> go.Figure:

    # Filter years
    df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

    # Filter genres (optional)
    if selected_genres_tuple:
        df = df[df["genre"].isin(list(selected_genres_tuple))]

    # Handle empty result
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Treemap (Year → Genre)",
            annotations=[dict(text="No data for the selected filters.", showarrow=False)],
            margin=dict(t=50, l=25, r=25, b=25),
        )
        return fig

    # Keep stable chronological order ONLY for colors
    years_sorted = sorted(df["year"].unique().tolist())

    # Aggregate mean popularity
    yg = df.groupby(["year", "genre"], as_index=False)["popularity"].mean()

    # Totals per year
    year_totals = yg.groupby("year", as_index=False)["popularity"].sum()

    # ---- ORDER BY VALUE (largest → smallest) ----
    year_totals_layout = year_totals.sort_values("popularity", ascending=False)

    labels, parents, values, ids = [], [], [], []

    ROOT_ID = "root"
    root_label = f"All Years ({years_sorted[0]}–{years_sorted[-1]})"

    ids.append(ROOT_ID)
    labels.append(root_label)
    parents.append("")
    values.append(float(year_totals["popularity"].sum()))

    # Year nodes
    for _, r in year_totals_layout.iterrows():
        y = int(r["year"])
        y_id = f"year:{y}"
        ids.append(y_id)
        labels.append(str(y))
        parents.append(ROOT_ID)
        values.append(float(r["popularity"]))

    # Genre nodes (largest → smallest within year)
    for y in year_totals_layout["year"].astype(int).tolist():
        yg_y = yg[yg["year"] == y].sort_values("popularity", ascending=False)
        for _, r in yg_y.iterrows():
            g = str(r["genre"])
            g_id = f"year:{y}|genre:{g}"
            ids.append(g_id)
            labels.append(g)
            parents.append(f"year:{y}")
            values.append(float(r["popularity"]))

    # -----------------------------
    # COLORS (UNCHANGED)
    # -----------------------------
    root_fill_color = "#444444"

    year_container_palette = [
        "rgb(255, 235, 215)",
        "rgb(215, 245, 230)",
        "rgb(220, 230, 255)",
        "rgb(255, 245, 210)",
        "rgb(235, 230, 245)",
        "rgb(230, 245, 255)",
        "rgb(245, 235, 255)",
        "rgb(240, 240, 240)",
    ]

    genre_palette = [
        "rgb(255, 176, 113)",
        "rgb(145, 227, 186)",
        "rgb(145, 175, 255)",
        "rgb(255, 226, 128)",
        "rgb(181, 163, 218)",
        "rgb(140, 210, 240)",
        "rgb(220, 170, 240)",
        "rgb(200, 200, 200)",
    ]

    year_to_container = {
        str(y): year_container_palette[i % len(year_container_palette)]
        for i, y in enumerate(years_sorted)
    }

    year_to_genre = {
        str(y): genre_palette[i % len(genre_palette)]
        for i, y in enumerate(years_sorted)
    }

    node_colors = []
    for node_id, p, lbl in zip(ids, parents, labels):
        if node_id == ROOT_ID:
            node_colors.append(root_fill_color)
        elif p == ROOT_ID:
            node_colors.append(year_to_container.get(str(lbl)))
        else:
            year = p.replace("year:", "")
            node_colors.append(year_to_genre.get(year))

    # -----------------------------
    # IMPROVED VISUAL SEPARATION
    # -----------------------------
    line_colors = []
    line_widths = []

    for node_id, p in zip(ids, parents):
        if node_id == ROOT_ID:
            line_colors.append("white")
            line_widths.append(3)
        elif p == ROOT_ID:
            # Year containers
            line_colors.append("rgba(0,0,0,0.6)")
            line_widths.append(4)
        else:
            # Genre leaves
            line_colors.append("rgba(255,255,255,0.9)")
            line_widths.append(1.5)

    node_text_colors = []
    for node_id, p in zip(ids, parents):
        if node_id == ROOT_ID:
            node_text_colors.append("white")
        elif p == ROOT_ID:
            node_text_colors.append("rgb(50,50,50)")
        else:
            node_text_colors.append("rgb(55,55,55)")

    fig = go.Figure(
        go.Treemap(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            sort=False,
            # Padding between tiles
            tiling=dict(packing="squarify", pad=4),
            marker=dict(
                colors=node_colors,
                line=dict(color=line_colors, width=line_widths),
            ),
            textfont=dict(color=node_text_colors, size=13),
            hovertemplate="<b>%{label}</b><br>Avg. Popularity: %{value:.1f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Treemap (Year → Genre) — Ordered by value",
        width=1000,
        height=700
    )

    return fig


# -----------------------------
# Streamlit render()
# -----------------------------
def render(df: pd.DataFrame, year_range: tuple, selected_genres: list) -> go.Figure:
    start_year, end_year = year_range
    return build_treemap_figure(df, start_year, end_year, tuple(selected_genres))