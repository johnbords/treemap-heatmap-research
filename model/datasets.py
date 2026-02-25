import pandas as pd

import streamlit as st

@st.cache_data(show_spinner=False)
def load_dataset(file_name: str) -> pd.DataFrame:
    df = pd.read_csv(file_name)
    df["genre"] = df["genre"].astype(str).str.split(",")
    df = df.explode("genre")
    df["genre"] = df["genre"].astype(str).str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    return df

@st.cache_data(show_spinner=False)
def load_genre_list(df: pd.DataFrame) -> list:
    genre_col = df["genre"].astype(str).str.split(",").tolist()
    genre_list = [g.strip() for genre_set in genre_col for g in genre_set]
    return sorted(dict.fromkeys(genre_list), key=str.lower)