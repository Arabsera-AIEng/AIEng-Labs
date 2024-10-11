import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Model Details", page_icon="🔍", layout="wide")

# Sample JSON data for models (replace with actual data)
json_data = {
    "projects": [
        {
            "project_name": "House Price Prediction",
            "algorithm": "Stacked Averaged Models",
            "rmse": 0.07844981595267218,
            "date_of_training": "2024-10-06 23:57:48",
            "stage": "prod",
            "hyperparameters": {"alpha": 0.0005, "max_depth": 4},
            "features": ["GrLivArea", "OverallQual", "YearBuilt", "TotalBsmtSF", "GarageCars"]
        },
        {
            "project_name": "Recommender System",
            "algorithm": "Collaborative Filtering",
            "rmse": 0.09234567890123456,
            "date_of_training": "2024-09-20 15:30:00",
            "features": ["UserID", "ItemID", "Rating"]
        }
    ]
}

# Get the URL parameter or session state to determine the selected project
query_params = st.query_params
project_name = query_params.get("project_name", None) or st.session_state.get("selected_model")

# Display project details if project_name is provided
if project_name:
    # Find the project in the JSON data
    project = next((proj for proj in json_data["projects"] if proj["project_name"] == project_name), None)

    if project:
        # Display Project Information
        st.title(f"Model Details: {project_name}")
        st.markdown(f"**Algorithm**: {project['algorithm']}")
        st.markdown(f"**RMSE**: {project['rmse']:.4f}")
        st.markdown(f"**Date of Training**: {project['date_of_training']}")

        # Display Stage Status
        stage = project.get("stage", "In Development")
        stage_color = "green" if stage == "prod" else "orange"
        st.markdown(
            f"<span style='color: white; background-color: {stage_color}; padding: 5px 10px; border-radius: 5px;'>{'Production' if stage == 'prod' else 'In Development'}</span>",
            unsafe_allow_html=True)

        # Display Hyperparameters (if any)
        st.subheader("Hyperparameters")
        hyperparams = project.get("hyperparameters", {})
        if hyperparams:
            st.json(hyperparams)
        else:
            st.write("No hyperparameters available.")

        # Display Feature List
        st.subheader("Feature List")
        features = project.get("features", [])
        if features:
            st.write(", ".join(features))
        else:
            st.write("No features available.")
    else:
        st.error(f"Project '{project_name}' not found in the catalog.")
else:
    st.warning("No project selected. Please navigate back to the Model Catalog and select a project.")
