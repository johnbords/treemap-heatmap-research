import streamlit as st

def render_page():
    # init page
    # The page_title param is for the page's tab title
    st.set_page_config(page_title="Treemap vs Heatmap", layout="wide")

    # Sets the Page title
    st.title("Treemap vs Heatmap")

if __name__ == "__main__":
    render_page()
