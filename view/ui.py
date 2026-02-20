import streamlit as st
import heatmap, treemap, fixed_sidebar
import pandas as pd
import quiz


def year_slider() -> tuple:
    return st.slider(
        "Year range",
        min_value=1998,
        max_value=2020,
        value=(1998, 2020),
        step=1
    )


def render_page():
    # ✅ MUST be the first Streamlit call (inside configure_sidebar)
    fixed_sidebar.configure_sidebar(
        page_title="Treemap vs Heatmap",
        layout="wide",
        expanded=True,
        lock=True,
        width_px=500,
    )

    # Load data for genre list
    df = pd.read_csv(r"C:\Users\Study\PycharmProjects\CS490R\treemap-heatmap-research\model\songs_normalize.csv")
    genre_col = df["genre"].astype(str).str.split(",")
    genre_col = genre_col.tolist()
    genre_list = [genre.strip() for genre_set in genre_col for genre in genre_set]
    genre_list = sorted(dict.fromkeys(genre_list), key=str.lower)

    # Sidebar quiz (stays visible)
    quiz.render_quiz()

    # Main page content
    st.title("Treemap vs Heatmap")
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    st.subheader("Filters")

    if ("year_range" in st.session_state) and ("genres" in st.session_state):
        if st.session_state.year_range is None:
            st.session_state.year_range = year_slider()
        if st.session_state.genres is None:
            st.session_state.genres = st.multiselect("Genre", genre_list)
    else:
        st.session_state.year_range = year_slider()
        st.session_state.genres = st.multiselect("Genre", genre_list)

    # ✅ 2-selection radio BETWEEN filters and chart
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    chart_type = st.radio(
        "Chart type",
        options=["Heatmap", "Treemap"],
        horizontal=True,
        key="chart_type_radio",
    )

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.subheader(f"Genre Popularity {chart_type}")

    if ("year_range" in st.session_state) and ("genres" in st.session_state):
        if (st.session_state.year_range is not None) and (st.session_state.genres is not None):
            # Render selected chart
            if chart_type == "Heatmap":
                fig = heatmap.render(st.session_state.year_range, st.session_state.genres)
            else:
                fig = treemap.render(st.session_state.year_range, st.session_state.genres)

        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    render_page()