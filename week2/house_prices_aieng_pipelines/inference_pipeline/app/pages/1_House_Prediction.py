import os
import json
import requests
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="House Prediction",
    page_icon="🏠",
    layout="wide",
)

# FastAPI endpoints
PREDICT_API_URL = "http://localhost:8000/api/predict"
SUBMIT_ACTUAL_API_URL = "http://localhost:8000/api/submit_actual"  # New endpoint for submitting actual price

# Load test data
@st.cache_data
def load_test_data():
    test_data = pd.read_csv('test.csv')
    return test_data

# Main content
st.title("House Price Prediction 🏠")
st.markdown("Predict the sale price of houses using our advanced machine learning model.")

# Divider
st.markdown("---")

# Load data
test_data = load_test_data()

# Session state management
if 'sample_input' not in st.session_state:
    st.session_state['sample_input'] = None
if 'predict_clicked' not in st.session_state:
    st.session_state['predict_clicked'] = False
if 'submit_actual_clicked' not in st.session_state:
    st.session_state['submit_actual_clicked'] = False

# Layout columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Generate a Random House")
    generate_btn = st.button("🔄 Generate Random House")

    if generate_btn:
        st.session_state['sample_input'] = test_data.sample(n=1).to_dict(orient='records')[0]
        st.session_state['predict_clicked'] = False  # Reset prediction state
        st.session_state['submit_actual_clicked'] = False  # Reset submit state

    if st.session_state['sample_input'] is not None:
        st.write("### Random House Features")
        with st.expander("View Features"):
            st.json(st.session_state['sample_input'])

        st.subheader("2. Predict Sale Price")
        predict_btn = st.button("💰 Predict Price")

        if predict_btn:
            st.session_state['predict_clicked'] = True

with col2:
    st.subheader("Prediction Result")
    if st.session_state.get('predict_clicked', False):
        sample_input = st.session_state['sample_input'].copy()

        # Handle NaN values in the input data by replacing them with None
        for key in sample_input:
            if isinstance(sample_input[key], float) and np.isnan(sample_input[key]):
                sample_input[key] = None

        # API request to predict price
        try:
            response = requests.post(PREDICT_API_URL, json={"data": sample_input})
            if response.status_code == 200:
                result = response.json()
                predicted_price = result.get("predicted_price", None)
                if predicted_price is not None:
                    st.success(f"**Predicted Sale Price:** ${predicted_price:,.2f}")
                    st.session_state['predicted_price'] = predicted_price  # Store predicted price in session state
                else:
                    st.error("Prediction failed. No predicted price returned.")
            else:
                st.error(f"Request failed with status code: {response.status_code}")
                st.error(f"Response: {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Generate a random house and click 'Predict Price' to see the result.")

# Show the input for actual price and submit button if prediction has been made
if st.session_state.get('predict_clicked', False):
    st.markdown("---")
    st.subheader("Submit Actual Sale Price")
    st.markdown(
        "<p style='color: #6D6875;'>If you have the actual sale price for this house, you can enter it below to help us improve our model.</p>",
        unsafe_allow_html=True,
    )

    # Input field for the actual sale price
    actual_price_input = st.number_input("Enter Actual Sale Price ($)", min_value=0, value=0, step=1000)

    # Submit button for actual price
    submit_actual_btn = st.button("📩 Submit Actual Sale Price")

    if submit_actual_btn:
        # Prepare the data for submission with timestamp
        actual_submission_data = {
            "features": st.session_state['sample_input'],
            "predicted_price": st.session_state['predicted_price'],
            "actual_price": actual_price_input,
            "timestamp": datetime.now().isoformat()  # Add the current timestamp
        }

        # Handle NaN values in the actual_submission_data by replacing them with None
        for key, value in actual_submission_data["features"].items():
            if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                actual_submission_data["features"][key] = None

        # API request to submit actual price
        try:
            submit_response = requests.post(SUBMIT_ACTUAL_API_URL, json=actual_submission_data)
            if submit_response.status_code == 200:
                submit_result = submit_response.json()
                rmsle_value = submit_result.get("rmsle", None)
                if rmsle_value is not None:
                    st.success(f"Thank you! Your actual price submission has been recorded. Current RMSLE: {rmsle_value:.4f}")
                else:
                    st.success("Thank you! Your actual price submission has been recorded.")
                st.session_state['submit_actual_clicked'] = True  # Mark submission as complete
            else:
                st.error(f"Submission failed with status code: {submit_response.status_code}")
                st.error(f"Response: {submit_response.text}")
        except Exception as e:
            st.error(f"An error occurred while submitting actual price: {str(e)}")

# Custom CSS to enhance button styles and overall appearance
st.markdown(
    """
    <style>
    .stButton > button {
        width: 100%;
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }
    </style>
    """,
    unsafe_allow_html=True
)
