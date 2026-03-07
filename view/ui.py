import os
from pathlib import Path

import streamlit as st
import plotly.graph_objs as go

from view import fixed_sidebar
from view import quiz

# -----------------------------
# Dataset uploader (persisted to disk)
# -----------------------------

def _get_persist_path() -> Path:
    p = st.session_state.get("dataset_persist_path")
    if not p:
        return Path("uploaded_dataset.csv").resolve()
    return Path(str(p)).resolve()



def _persist_uploaded_csv(uploaded_file) -> None:
    persist_path = _get_persist_path()
    persist_path.parent.mkdir(parents=True, exist_ok=True)
    persist_path.write_bytes(uploaded_file.getvalue())



def dataset_uploader() -> None:
    """Uploader UI. When a CSV is uploaded, save it and force a full rerun."""
    uploaded = st.file_uploader(
        "Dataset (CSV)",
        type=["csv"],
        key="dataset_file_uploader",
        help="Upload the CSV dataset used by the heatmap/treemap.",
    )

    if uploaded is None:
        return

    fingerprint = (uploaded.name, getattr(uploaded, "size", None))
    if st.session_state.get("_dataset_last_upload") == fingerprint:
        return

    st.session_state["_dataset_last_upload"] = fingerprint
    _persist_uploaded_csv(uploaded)

    for k in ["genres", "genres_ms"]:
        if k in st.session_state:
            del st.session_state[k]

    st.rerun()


# -----------------------------
# Typography settings
# -----------------------------

def _init_typography_state() -> None:
    st.session_state.setdefault("font_family", "Sans Serif")
    st.session_state.setdefault("font_size_px", 16)
    st.session_state.setdefault("hover_font_size_px", 16)



def _font_family_css(font_family_label: str) -> str:
    mapping = {
        "Sans Serif": "Arial, Helvetica, sans-serif",
        "Serif": '"Times New Roman", Times, serif',
        "Monospace": '"Courier New", Courier, monospace',
    }
    return mapping.get(font_family_label, mapping["Sans Serif"])



def _inject_typography_css() -> None:
    _init_typography_state()
    font_family = _font_family_css(st.session_state.get("font_family", "Sans Serif"))
    font_size = int(st.session_state.get("font_size_px", 16))

    st.markdown(
        f"""
        <style>
        div.block-container,
        [data-testid="stSidebar"] .block-container {{
            font-family: {font_family};
            font-size: {font_size}px;
        }}

        div.block-container p,
        div.block-container label,
        div.block-container li,
        div.block-container .stMarkdown,
        div.block-container .stCaption,
        div.block-container [data-testid="stMetricValue"],
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] li,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .stCaption {{
            font-family: {font_family};
            font-size: {font_size}px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def typography_settings() -> None:
    _init_typography_state()

    st.selectbox(
        "Font style",
        options=["Sans Serif", "Serif", "Monospace"],
        key="font_family",
    )

    st.slider(
        "Font size",
        min_value=10,
        max_value=28,
        key="font_size_px",
    )

    st.slider(
        "Hover tooltip font size",
        min_value=10,
        max_value=28,
        key="hover_font_size_px",
    )

def settings_expander(on_change_func=None, expanded=False, show_chart_type=True) -> None:
    _init_typography_state()

    with st.expander("⚙ Settings", expanded=expanded):
        if show_chart_type:
            st.radio(
                "Chart type",
                options=["Heatmap", "Treemap"],
                horizontal=True,
                key="chart_type_radio",
                on_change=on_change_func,
            )
            st.divider()

        typography_settings()
        st.divider()
        dataset_uploader()



def render_no_data_page() -> None:
    """Shown when the app runs but no CSV has been uploaded yet."""
    fixed_sidebar.configure_sidebar(
        page_title="Treemap vs Heatmap",
        layout="wide",
        expanded=True,
        lock=False,
        width_px=500,
    )

    _inject_typography_css()

    st.title("Treemap vs Heatmap")
    st.warning("No data to show. Upload the dataset first.")

    spacer, controls = st.columns([6, 1])
    with controls:
        settings_expander(expanded=True, show_chart_type=False)


# -----------------------------
# Year filter (selectboxes)
# -----------------------------

def _sync_year_and_fire(on_change_func):
    override = st.session_state.get("year_filter_override")
    yf = st.session_state.get("year_from")

    if yf is None:
        return

    if override and override.get("mode") == "single":
        st.session_state.year_to = yf
        st.session_state.year_range = (yf, yf)
    else:
        yt = st.session_state.get("year_to")
        if yt is None:
            return
        if yf > yt:
            return
        st.session_state.year_range = (yf, yt)

    if on_change_func:
        on_change_func()



def year_selectbox(on_change_func):
    st.markdown("### 📅 Year Range")

    years = list(range(1998, 2021))

    if "year_range" not in st.session_state:
        st.session_state.year_range = (1998, 2020)

    override = st.session_state.get("year_filter_override")

    if "year_from" not in st.session_state:
        st.session_state.year_from = None
    if "year_to" not in st.session_state:
        st.session_state.year_to = None

    if override and override.get("mode") == "single":
        st.session_state.year_to = st.session_state.year_from

    if override and override.get("mode") == "single":
        col_from, _ = st.columns([1, 7])
        with col_from:
            from_year = st.selectbox(
                "Year",
                options=years,
                placeholder="Select a year",
                key="year_from",
                label_visibility="collapsed",
                on_change=lambda: _sync_year_and_fire(on_change_func),
            )

        if from_year is None:
            return

        st.session_state.year_to = from_year
        st.session_state.year_range = (from_year, from_year)
        return

    col_from, col_dash, col_to, _ = st.columns([1, 0.3, 1, 6])

    with col_from:
        from_year = st.selectbox(
            "From year",
            options=years,
            placeholder="From",
            key="year_from",
            label_visibility="collapsed",
            on_change=lambda: _sync_year_and_fire(on_change_func),
        )

    with col_dash:
        st.markdown(
            "<div style='text-align:center;padding-top:8px;'>—</div>",
            unsafe_allow_html=True,
        )

    with col_to:
        to_year = st.selectbox(
            "To year",
            options=years,
            placeholder="To",
            key="year_to",
            label_visibility="collapsed",
            on_change=lambda: _sync_year_and_fire(on_change_func),
        )

    if from_year is None or to_year is None:
        return

    if from_year > to_year:
        st.warning("Invalid year range. Try to pick another year")
        return

    st.session_state.year_range = (from_year, to_year)


# -----------------------------
# Genre filter (buttons + multiselect + checkboxes)
# -----------------------------

def genre_filters(
    genre_list: list,
    on_change_func=None,
    columns: int = 2,
    bordered: bool = True,
    show_select_controls: bool = True,
):
    st.markdown(
        """
        <style>
        div[data-testid="stCheckbox"] { margin-bottom: 0.15rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    genres_sorted = sorted(genre_list, key=lambda s: str(s).lower())

    if "genres" not in st.session_state:
        st.session_state.genres = []

    if "genres_ms" not in st.session_state:
        st.session_state.genres_ms = []

    for g in genres_sorted:
        k = f"genre_{g}"
        if k not in st.session_state:
            st.session_state[k] = False

    def _compute_union() -> list:
        ms = set(st.session_state.get("genres_ms", []))
        checked = {g for g in genres_sorted if st.session_state.get(f"genre_{g}", False)}
        combined = ms | checked
        return [g for g in genres_sorted if g in combined]

    def _update_final_and_fire():
        st.session_state.genres = _compute_union()
        if on_change_func:
            on_change_func()

    st.markdown("### Genre")

    host = st.container(border=True) if bordered else st.container()
    with host:
        if show_select_controls:
            # c1, c2, _ = st.columns([1, 1, 10])
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Select All", width='stretch'):
                    st.session_state.genres_ms = genres_sorted[:]
                    for g in genres_sorted:
                        st.session_state[f"genre_{g}"] = True
                    _update_final_and_fire()
                    st.rerun()

            with c2:
                if st.button("Clear All", width='stretch'):
                    st.session_state.genres_ms = []
                    for g in genres_sorted:
                        st.session_state[f"genre_{g}"] = False
                    _update_final_and_fire()
                    st.rerun()

            st.divider()

        st.multiselect(
            "Genre (Multi-select)",
            options=genres_sorted,
            key="genres_ms",
            on_change=_update_final_and_fire,
        )

        st.divider()

        total = len(genres_sorted)
        rows_per_col = (total + columns - 1) // columns
        cols = st.columns(columns)

        for col_idx in range(columns):
            start = col_idx * rows_per_col
            end = min(start + rows_per_col, total)
            chunk = genres_sorted[start:end]

            with cols[col_idx]:
                for g in chunk:
                    st.checkbox(
                        g,
                        key=f"genre_{g}",
                        on_change=_update_final_and_fire,
                    )

    st.session_state.genres = _compute_union()
    return st.session_state.genres


# -----------------------------
# Page renderer
# -----------------------------

def render_page(fig: go.Figure, on_change_func, genre_list: list) -> None:
    fixed_sidebar.configure_sidebar(
        page_title="Treemap vs Heatmap",
        layout="wide",
        expanded=True,
        lock=False,
        width_px=500,
    )

    if "chart_type_radio" not in st.session_state:
        st.session_state.chart_type_radio = "Heatmap"

    _inject_typography_css()

    quiz.render_quiz()

    st.title("Treemap vs Heatmap")
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    st.subheader("Filters")

    year_selectbox(on_change_func)

    genre_filters(
        genre_list,
        on_change_func,
        columns=2,
    )

    chart_type = st.session_state.chart_type_radio

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.subheader(f"Genre Popularity {chart_type}")

    st.plotly_chart(fig, width="stretch")

    sp1, sp2, sp3 , controls = st.columns([0.5, 0.5, 0.5, 1])
    with controls:
        settings_expander(on_change_func=on_change_func, expanded=False, show_chart_type=True)
