from controller.main_controller import run_app
from model import datasets as ds
from view import ui
import streamlit as st

import os
import sys
from pathlib import Path


def _app_dir() -> Path:
    """Folder beside the executable (PyInstaller) or beside this file (dev)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def main():
    # Persist the uploaded CSV beside the app
    persist_path = _app_dir() / "uploaded_dataset.csv"
    st.session_state["dataset_persist_path"] = str(persist_path)

    # If no dataset yet, show a minimal page (no sidebar content)
    if not persist_path.exists():
        ui.render_no_data_page()
        return

    # Load dataset
    df = ds.load_dataset(str(persist_path))
    genre_list = ds.load_genre_list(df)

    # Keep a valid default year range
    yr = st.session_state.get("year_range", (1998, 2020))
    if not yr or yr[0] is None or yr[1] is None:
        st.session_state.year_range = (1998, 2020)

    run_app(df, genre_list)


if __name__ == "__main__":
    main()
