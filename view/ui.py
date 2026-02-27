import streamlit as st

from view import fixed_sidebar
from view import quiz
import plotly.graph_objs as go


# -----------------------------
# Widgets
# -----------------------------
# def year_slider(on_change_func) -> tuple:
#     return st.slider(
#         "Year range",
#         min_value=1998,
#         max_value=2020,
#         step=1,
#         key="year_range",
#         on_change=on_change_func,
#     )

def _sync_and_fire(on_change_func):
    st.session_state.year_range = (st.session_state.year_from, st.session_state.year_to)
    if st.session_state.year_from > st.session_state.year_to:
        return
    if on_change_func:
        on_change_func()

def year_selectbox(on_change_func):
    st.markdown("### 📅 Year Range")

    years = list(range(1998, 2021))

    # Unified state (like your old slider key)
    if "year_range" not in st.session_state:
        st.session_state.year_range = (1998, 2020)

    # Set widget defaults ONLY if they don't exist yet (before widget creation)
    if "year_from" not in st.session_state:
        st.session_state.year_from = st.session_state.year_range[0]
    if "year_to" not in st.session_state:
        st.session_state.year_to = st.session_state.year_range[1]

    # Left-aligned compact layout
    col_from, col_dash, col_to, _ = st.columns([1, 0.3, 1, 6])

    with col_from:
        from_year = st.selectbox(
            "",
            years,
            key="year_from",
            label_visibility="collapsed",
            on_change=lambda: _sync_and_fire(on_change_func),
        )

    with col_dash:
        st.markdown("<div style='text-align:center;padding-top:8px;'>—</div>", unsafe_allow_html=True)

    with col_to:
        to_year = st.selectbox(
            "",
            years,
            key="year_to",
            label_visibility="collapsed",
            on_change=lambda: _sync_and_fire(on_change_func),
        )

    if from_year > to_year:
        st.error("Invalid year range")
        st.stop()

    # Keep unified state consistent
    st.session_state.year_range = (from_year, to_year)

def render_page(fig: go.Figure, on_change_func, genre_list: list) -> None:
    # ✅ MUST be the first Streamlit call (inside configure_sidebar)
    fixed_sidebar.configure_sidebar(
        page_title="Treemap vs Heatmap",
        layout="wide",
        expanded=True,
        lock=True,
        width_px=500,
    )

    # Sidebar quiz (stays visible)
    quiz.render_quiz()

    # Main page content
    st.title("Treemap vs Heatmap")
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    st.subheader("Filters")

    year_selectbox(on_change_func)

    st.multiselect(
        "Genre",
        genre_list,
        key="genres",
        on_change=on_change_func,
    )

    # ✅ 2-selection radio BETWEEN filters and chart
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    chart_type = st.radio(
        "Chart type",
        options=["Heatmap", "Treemap"],
        horizontal=True,
        key="chart_type_radio",
        on_change=on_change_func,
    )

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.subheader(f"Genre Popularity {chart_type}")

    st.plotly_chart(fig, use_container_width=True)


# if __name__ == "__main__":
#     render_page()