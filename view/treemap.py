import pandas as pd
import plotly.graph_objs as go

def render_treemap():
    # --- Load your CSV ---
    df = pd.read_csv("C:\\Users\\Study\\PycharmProjects\\CS490R\\treemap-heatmap-research\\model\\1998-2002.csv")
    labels, parents, values, ids = [], [], [], []

    # mean popularity per (year, genre)
    yg = df.groupby(["year", "genre"], as_index=False)["popularity"].mean()

    # year totals (must equal sum of children when branchvalues="total")
    year_totals = yg.groupby("year", as_index=False)["popularity"].sum()

    # --- Year nodes ---
    for _, r in year_totals.iterrows():
        y = int(r["year"])
        y_id = f"year:{y}"

        ids.append(y_id)
        labels.append(str(y))
        parents.append("")  # root
        values.append(float(r["popularity"]))

    # --- Genre nodes (unique per year) ---
    for _, r in yg.iterrows():
        y = int(r["year"])
        g = str(r["genre"])
        g_id = f"year:{y}|genre:{g}"

        ids.append(g_id)
        labels.append(g)
        parents.append(f"year:{y}")  # parent is the YEAR id
        values.append(float(r["popularity"]))

    fig = go.Figure(go.Treemap(
        ids=ids,
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        root_color="lightgrey",
        hovertemplate="<b>%{label}</b><br>Value: %{value}<extra></extra>",
    ))

    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    fig.show()

if __name__ == "__main__":
    render_treemap()