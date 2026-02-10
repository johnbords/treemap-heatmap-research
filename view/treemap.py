import pandas as pd
import plotly.graph_objs as go


def render_treemap():
    # --- Load your CSV ---
    df = pd.read_csv(
        r"C:\Users\Study\PycharmProjects\CS490R\treemap-heatmap-research\model\1998-2002.csv"
    )

    # ------------------------------------------------------------
    # Split multi-genre entries (e.g., "hip hop, pop, R&B")
    # into separate rows so that each genre is treated as its
    # own category. This ensures genre categories are consistent
    # across treemap and heatmap conditions.
    # ------------------------------------------------------------
    df["genre"] = df["genre"].str.split(",")
    df = df.explode("genre")
    df["genre"] = df["genre"].str.strip()

    # --- Aggregate: mean popularity per (year, genre) ---
    yg = df.groupby(["year", "genre"], as_index=False)["popularity"].mean()

    # Stable ordering: year ascending, genre alphabetical
    yg = yg.sort_values(["year", "genre"], ascending=[True, True])

    # Year totals must equal sum(children) when branchvalues="total"
    year_totals = (
        yg.groupby("year", as_index=False)["popularity"]
        .sum()
        .sort_values("year", ascending=True)
    )

    labels, parents, values, ids = [], [], [], []

    # -----------------------------
    # EXPLICIT ROOT NODE (so you can color + hover it)
    # -----------------------------
    ROOT_ID = "root"

    yr_column = df['year'].unique()

    root_label = f"All Years ({min(yr_column)}–{max(yr_column)})"

    ids.append(ROOT_ID)
    labels.append(root_label)
    parents.append("")  # root has no parent
    values.append(float(year_totals["popularity"].sum()))  # >= sum of year nodes

    # --- Year nodes (children of ROOT_ID) ---
    for _, r in year_totals.iterrows():
        y = int(r["year"])
        y_id = f"year:{y}"

        ids.append(y_id)
        labels.append(str(y))
        parents.append(ROOT_ID)
        values.append(float(r["popularity"]))

    # --- Genre nodes (children of year nodes) ---
    for _, r in yg.iterrows():
        y = int(r["year"])
        g = str(r["genre"])
        g_id = f"year:{y}|genre:{g}"

        ids.append(g_id)
        labels.append(g)
        parents.append(f"year:{y}")
        values.append(float(r["popularity"]))

    # ------------------------------------------------
    # Pastel colors: root + year containers + children
    # ------------------------------------------------
    root_fill_color = "#444444"  # outermost box fill

    year_color_list = [
        "rgb(255, 235, 215)",
        "rgb(215, 245, 230)",
        "rgb(220, 230, 255)",
        "rgb(255, 245, 210)",
        "rgb(235, 230, 245)",
    ]

    genre_fill_color_list = [
        "rgb(255, 176, 113)",
        "rgb(145, 227, 186)",
        "rgb(145, 175, 255)",
        "rgb(255, 226, 128)",
        "rgb(181, 163, 218)",
    ]

    year_container_colors = {
        str(yr): color for yr, color in zip(yr_column, year_color_list)
    }

    genre_fill_colors = {
        str(yr): color for yr, color in zip(yr_column, genre_fill_color_list)
    }

    node_colors = []
    for node_id, p, lbl in zip(ids, parents, labels):
        if node_id == ROOT_ID:
            node_colors.append(root_fill_color)
        elif p == ROOT_ID:
            node_colors.append(year_container_colors.get(str(lbl), "rgb(235,235,235)"))
        else:
            year = p.replace("year:", "")
            node_colors.append(genre_fill_colors.get(year, "rgb(230,230,230)"))

    # ------------------------------------------------
    # Text colors: edit ROOT label color specifically
    # ------------------------------------------------
    node_text_colors = []
    for node_id, p in zip(ids, parents):
        if node_id == ROOT_ID:
            node_text_colors.append("white")   # ROOT label color
        elif p == ROOT_ID:
            node_text_colors.append("rgb(50,50,50)")   # year labels
        else:
            node_text_colors.append("rgb(55,55,55)")   # genre labels

    fig = go.Figure(go.Treemap(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",

        # keep year order stable (don’t reorder by values)
        sort=False,
        tiling=dict(packing="squarify"),

        marker=dict(
            colors=node_colors,
            line=dict(color="white", width=1),
        ),
        textfont=dict(
            color=node_text_colors,
            size=13,
        ),
        hovertemplate="<b>%{label}</b><br>Avg. Popularity: %{value}<extra></extra>",
    ))

    fig.update_layout(
        title="Treemap (Year → Genre) — Years ordered by time",
        margin=dict(t=50, l=25, r=25, b=25),
    )

    fig.show()


if __name__ == "__main__":
    render_treemap()