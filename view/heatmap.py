import streamlit as st
import pandas as pd
import plotly.graph_objs as go

@st.cache_data(show_spinner=False)
def load_songs():
    df = pd.read_csv(r"C:\Users\Study\PycharmProjects\CS490R\treemap-heatmap-research\model\songs_normalize.csv")
    df["genre"] = df["genre"].astype(str).str.split(",")
    df = df.explode("genre")
    df["genre"] = df["genre"].astype(str).str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    return df

@st.cache_data(show_spinner=False)
def build_heatmap_matrix(start_year: int, end_year: int, selected_genres_tuple: tuple):
    df = load_songs()

    df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]
    if selected_genres_tuple:
        df = df[df["genre"].isin(list(selected_genres_tuple))]

    heatmap_df = df.groupby(["genre", "year"], as_index=False)["popularity"].mean()
    heatmap_df["year"] = heatmap_df["year"].astype(str)

    return heatmap_df.pivot(index="genre", columns="year", values="popularity")

def render(year_range: tuple, selected_genres: list) -> go.Figure:
    start_year, end_year = year_range
    heatmap_matrix = build_heatmap_matrix(start_year, end_year, tuple(selected_genres))

    fig = go.Figure(go.Heatmap(
        x=heatmap_matrix.columns,
        y=heatmap_matrix.index,
        z=heatmap_matrix.values,
        colorscale="Sunset",
        colorbar=dict(title="Avg Popularity"),
        hovertemplate="Year: %{x}<br>Genre: %{y}<br>Avg Popularity: %{z:.1f}<extra></extra>",
        hoverongaps=False
    ))

    fig.update_layout(
        title="Average Song Popularity by Genre and Year",
        xaxis_title="Year",
        yaxis_title="Genre",
        width=1000,
        height=700
    )
    return fig