import streamlit as st
import json
# -----------------------------
# URL persistence helpers
# -----------------------------
def _load_state_from_url():
    """
    Hydrate st.session_state from URL query params (survives browser refresh / F5).
    """
    qp = st.query_params

    # year_range
    if "year_range" not in st.session_state:
        if "year" in qp and qp["year"]:
            try:
                a, b = str(qp["year"]).split(",")
                st.session_state.year_range = (int(a), int(b))
            except Exception:
                st.session_state.year_range = (1998, 2020)
        else:
            st.session_state.year_range = (1998, 2020)

    # genres (JSON list in URL)
    if "genres" not in st.session_state:
        if "genres" in qp and qp["genres"]:
            try:
                st.session_state.genres = json.loads(str(qp["genres"]))
            except Exception:
                st.session_state.genres = []
        else:
            st.session_state.genres = []

    # (optional) chart type
    if "chart_type_radio" not in st.session_state:
        if "chart" in qp and qp["chart"] in ("Heatmap", "Treemap"):
            st.session_state.chart_type_radio = qp["chart"]
        else:
            st.session_state.chart_type_radio = "Heatmap"

def _save_state_to_url():
    """
    Push current st.session_state -> URL query params.
    """
    yr = st.session_state.get("year_range", (1998, 2020))
    st.query_params["year"] = f"{yr[0]},{yr[1]}"

    genres = st.session_state.get("genres", [])
    st.query_params["genres"] = json.dumps(genres)

    chart = st.session_state.get("chart_type_radio", "Heatmap")
    st.query_params["chart"] = chart