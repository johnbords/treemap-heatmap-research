import streamlit as st
import pandas as pd
import plotly.graph_objs as go


def _font_family_css(font_family_label: str) -> str:
    mapping = {
        "Sans Serif": "Arial, Helvetica, sans-serif",
        "Serif": '"Times New Roman", Times, serif',
        "Monospace": '"Courier New", Courier, monospace',
    }
    return mapping.get(font_family_label, mapping["Sans Serif"])


@st.cache_data(show_spinner=False)
def build_heatmap_matrix(df: pd.DataFrame, start_year: int, end_year: int, selected_genres_tuple: tuple):
    df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]
    if selected_genres_tuple:
        df = df[df["genre"].isin(list(selected_genres_tuple))]

    heatmap_df = df.groupby(["genre", "year"], as_index=False)["popularity"].mean()
    heatmap_df["year"] = heatmap_df["year"].astype(str)

    return heatmap_df.pivot(index="genre", columns="year", values="popularity")


def render(df: pd.DataFrame, year_range: tuple, selected_genres: list) -> go.Figure:
    start_year, end_year = year_range
    heatmap_matrix = build_heatmap_matrix(df, start_year, end_year, tuple(selected_genres))

    font_size = int(st.session_state.get("font_size_px", 16))
    hover_font_size = int(st.session_state.get("hover_font_size_px", 16))
    font_family = _font_family_css(st.session_state.get("font_family", "Sans Serif"))

    axis_tick_size = max(10, font_size)
    axis_title_size = max(11, font_size + 1)
    chart_title_size = max(12, font_size + 2)
    colorbar_tick_size = max(10, font_size)
    colorbar_title_size = max(11, font_size + 1)

    fig = go.Figure(
        go.Heatmap(
            x=heatmap_matrix.columns,
            y=heatmap_matrix.index,
            z=heatmap_matrix.values,
            colorscale="Sunset",
            colorbar=dict(
                title=dict(
                    text="Avg Popularity",
                    font=dict(size=colorbar_title_size, family=font_family),
                ),
                tickfont=dict(size=colorbar_tick_size, family=font_family),
            ),
            hovertemplate="Year: %{x}<br>Genre: %{y}<br>Avg Popularity: %{z:.1f}<extra></extra>",
            hoverongaps=False,
            hoverlabel=dict(font=dict(size=hover_font_size, family=font_family)),
        )
    )

    fig.update_layout(
        title=dict(
            text="Average Song Popularity by Genre and Year",
            font=dict(size=chart_title_size, family=font_family),
        ),
        xaxis=dict(
            type="category",
            title=dict(text="Year", font=dict(size=axis_title_size, family=font_family)),
            tickfont=dict(size=axis_tick_size, family=font_family),
        ),
        yaxis=dict(
            title=dict(text="Genre", font=dict(size=axis_title_size, family=font_family)),
            tickfont=dict(size=axis_tick_size, family=font_family),
        ),
        width=1000,
        height=700,
        font=dict(size=font_size, family=font_family),
        hoverlabel=dict(font=dict(size=hover_font_size, family=font_family)),
    )
    return fig
