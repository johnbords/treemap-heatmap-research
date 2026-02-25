import streamlit as st

from view import fixed_sidebar
from view import quiz
import plotly.graph_objs as go


# -----------------------------
# Widgets
# -----------------------------
def year_slider(on_change_func) -> tuple:
    return st.slider(
        "Year range",
        min_value=1998,
        max_value=2020,
        step=1,
        key="year_range",
        on_change=on_change_func,
    )

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

    year_slider(on_change_func)

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