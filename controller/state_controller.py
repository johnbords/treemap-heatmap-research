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

    # --- year_range from URL (or default) ---
    if "year_range" not in st.session_state:
        if "year" in qp and qp["year"]:
            try:
                a, b = str(qp["year"]).split(",")
                st.session_state.year_range = (int(a), int(b))
            except Exception:
                st.session_state.year_range = (1998, 2020)
        else:
            st.session_state.year_range = (1998, 2020)

    # --- hydrate selectbox UI keys to match enforced filter ---
    # Do this even if year_range already existed (refresh, rerun, etc.)
    y1, y2 = st.session_state.year_range

    # Only set if missing (prevents overwriting user mid-selection)
    if "year_from" not in st.session_state or st.session_state.year_from is None:
        st.session_state.year_from = y1
    if "year_to" not in st.session_state or st.session_state.year_to is None:
        st.session_state.year_to = y2

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
    Compatible with selectbox-based year filter.
    """

    # Prefer unified tuple if available
    if "year_range" in st.session_state:
        yr = st.session_state.year_range
    else:
        # Fallback in case tuple not yet initialized
        yr = (
            st.session_state.get("year_from", 1998),
            st.session_state.get("year_to", 2020),
        )

    st.query_params["year"] = f"{yr[0]},{yr[1]}"

    genres = st.session_state.get("genres", [])
    st.query_params["genres"] = json.dumps(genres)

    chart = st.session_state.get("chart_type_radio", "Heatmap")
    st.query_params["chart"] = chart