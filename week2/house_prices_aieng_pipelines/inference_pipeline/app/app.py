import streamlit as st

# Set the page configuration
st.set_page_config(
    page_title="House Price Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Welcome to the House Price Predictor App 🏠💰")
st.markdown(
    """
    This application allows you to predict house prices and explore various aspects of the model and data.
    Use the navigation menu on the left to explore different sections.
    """
)
