import streamlit as st
import pandas as pd
import plotly.graph_objs as go


# -----------------------------
# Shared loader (same as heatmap)
# -----------------------------
@st.cache_data(show_spinner=False)
def load_songs():
    df = pd.read_csv(
        r"C:\Users\Study\PycharmProjects\CS490R\treemap-heatmap-research\model\songs_normalize.csv"
    )
    df["genre"] = df["genre"].astype(str).str.split(",")
    df = df.explode("genre")
    df["genre"] = df["genre"].astype(str).str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    return df


# -----------------------------
# Treemap builder w/ filters
# -----------------------------
@st.cache_data(show_spinner=False)
def build_treemap_figure(
    start_year: int,
    end_year: int,
    selected_genres_tuple: tuple,
) -> go.Figure:
    df = load_songs()

    # Filter years
    df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

    # Filter genres (optional)
    if selected_genres_tuple:
        df = df[df["genre"].isin(list(selected_genres_tuple))]

    # Handle empty result after filters
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Treemap (Year → Genre)",
            annotations=[dict(text="No data for the selected filters.", showarrow=False)],
            margin=dict(t=50, l=25, r=25, b=25),
        )
        return fig

    years_sorted = sorted(df["year"].unique().tolist())

    # Aggregate mean popularity per (year, genre)
    yg = df.groupby(["year", "genre"], as_index=False)["popularity"].mean()
    yg = yg.sort_values(["year", "genre"], ascending=[True, True])

    # Totals per year must equal sum(children) for branchvalues="total"
    year_totals = (
        yg.groupby("year", as_index=False)["popularity"]
        .sum()
        .sort_values("year", ascending=True)
    )

    labels, parents, values, ids = [], [], [], []

    # Root node
    ROOT_ID = "root"
    root_label = f"All Years ({years_sorted[0]}–{years_sorted[-1]})"
    ids.append(ROOT_ID)
    labels.append(root_label)
    parents.append("")
    values.append(float(year_totals["popularity"].sum()))

    # Year nodes
    for _, r in year_totals.iterrows():
        y = int(r["year"])
        y_id = f"year:{y}"
        ids.append(y_id)
        labels.append(str(y))
        parents.append(ROOT_ID)
        values.append(float(r["popularity"]))

    # Genre nodes
    for _, r in yg.iterrows():
        y = int(r["year"])
        g = str(r["genre"])
        g_id = f"year:{y}|genre:{g}"
        ids.append(g_id)
        labels.append(g)
        parents.append(f"year:{y}")
        values.append(float(r["popularity"]))

    # Colors (cycle for arbitrary #years)
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
            node_colors.append(year_to_container.get(str(lbl), "rgb(235,235,235)"))
        else:
            year = p.replace("year:", "")
            node_colors.append(year_to_genre.get(year, "rgb(230,230,230)"))

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
            tiling=dict(packing="squarify"),
            marker=dict(colors=node_colors, line=dict(color="white", width=1)),
            textfont=dict(color=node_text_colors, size=13),
            hovertemplate="<b>%{label}</b><br>Avg. Popularity: %{value:.1f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Treemap (Year → Genre) — Years ordered by time",
        width=1000,
        height=700
    )

    return fig


# -----------------------------
# Streamlit-facing render()
# -----------------------------
def render(year_range: tuple, selected_genres: list) -> go.Figure:
    start_year, end_year = year_range
    fig = build_treemap_figure(start_year, end_year, tuple(selected_genres))
    return fig