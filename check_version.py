import streamlit as st
st.write("streamlit version:", st.__version__)
st.write("has v2:", hasattr(st.components, "v2") and hasattr(st.components.v2, "component"))