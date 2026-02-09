import pandas as pd
import plotly.graph_objs as go

def render_heatmap():

    # Load data
    df = pd.read_csv("C:\\Users\\Study\\PycharmProjects\\CS490R\\treemap-heatmap-research\\model\\1998-2002.csv")

    # Split genres into separate rows
    # explode(): splits a single cell containing multiple values (e.g., a list of genres)
    # into multiple rows, duplicating the rest of the row so each value gets its own row
    df["genre"] = df["genre"].str.split(", ")
    df = df.explode("genre")

    # Aggregate: average popularity per year per genre
    heatmap_df = (
        df.groupby(["genre", "year"])["popularity"]
        .mean()
        .reset_index()
    )

    # Pivot to matrix form (required for go.Heatmap)
    heatmap_matrix = heatmap_df.pivot(
        index="genre",
        columns="year",
        values="popularity"
    )

    # Create heatmap
    fig = go.Figure(
        data=go.Heatmap(
            x=heatmap_matrix.columns,
            y=heatmap_matrix.index,
            z=heatmap_matrix.values,
            colorscale="Sunset",
            colorbar=dict(title="Avg Popularity"),

            hovertemplate=(
                "Year: %{x}<br>"
                "Genre: %{y}<br>"
                "Avg Popularity: %{z:.1f}"
                "<extra></extra>"
            ),
            hoverongaps=False,
        )
    )

    # Layout
    fig.update_layout(
        title="Average Song Popularity by Genre and Year",
        xaxis_title="Year",
        yaxis_title="Genre",

        # Make NaN cells appear white
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    fig.show()

if __name__ == "__main__":
    render_heatmap()