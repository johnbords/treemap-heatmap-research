from view import ui, heatmap, treemap
from controller import state_controller as sc
import streamlit as st
import pandas as pd

def run_app(df: pd.DataFrame, genre_list: list):
    # ✅ Load persisted state (survives F5 refresh)
    sc._load_state_from_url()

    # Render selected chart
    if st.session_state.chart_type_radio == "Heatmap":
        fig = heatmap.render(df, st.session_state.year_range, st.session_state.genres)
    else:
        fig = treemap.render(df, st.session_state.year_range, st.session_state.genres)

    ui.render_page(fig, on_change_func=sc._save_state_to_url, genre_list=genre_list)

# if __name__ == "__main__":
#     run_app()