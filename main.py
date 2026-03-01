from controller.main_controller import run_app
from model import datasets as ds
import streamlit as st

def main():
    file_name = r"C:\Users\Study\PycharmProjects\CS490R\treemap-heatmap-research\model\songs_normalize.csv"

    df = ds.load_dataset(file_name)

    genre_list = ds.load_genre_list(df)

    yr = st.session_state.get("year_range", (1998, 2020))
    if not yr or yr[0] is None or yr[1] is None:
        st.session_state.year_range = (1998, 2020)

    run_app(df, genre_list)

if __name__ == "__main__":
    main()