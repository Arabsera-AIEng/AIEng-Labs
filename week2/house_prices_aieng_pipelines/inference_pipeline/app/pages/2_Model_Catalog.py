import streamlit as st
import pandas as pd
from streamlit.components.v1 import html

# Set page configuration with a wide layout and title
st.set_page_config(page_title="Model Catalog", page_icon="📚", layout="wide")

# Sample JSON data for demonstration purposes (replace with your actual data source)
json_data = {
    "projects": [
        {
            "project_name": "House Price Prediction",
            "algorithm": "Stacked Averaged Models",
            "rmse": 0.0784,
            "date_of_training": "2024-10-06 23:57:48",
            "stage": "prod",
            "hyperparameters": {"alpha": 0.0005, "max_depth": 4},
            "features": ["GrLivArea", "OverallQual", "YearBuilt", "TotalBsmtSF", "GarageCars"]
        },
        {
            "project_name": "Recommender System",
            "algorithm": "Collaborative Filtering",
            "rmse": 0.0923,
            "date_of_training": "2024-09-20 15:30:00",
            "stage": "dev",
            "features": ["UserID", "ItemID", "Rating"]
        }
    ]
}

# Convert JSON data to DataFrame for easier manipulation
df = pd.DataFrame(json_data["projects"])

# Function to determine the status style based on the model stage
def get_status_style(stage):
    if stage == "prod":
        return "Production", "#28a745"  # Green for production
    else:
        return "In Development", "#ffc107"  # Orange for development

# Function for navigation using the hack
def nav_page(page_name, timeout_secs=3):
    nav_script = """
        <script type="text/javascript">
            function attempt_nav_page(page_name, start_time, timeout_secs) {
                var links = window.parent.document.getElementsByTagName("a");
                for (var i = 0; i < links.length; i++) {
                    if (links[i].href.toLowerCase().endsWith("/" + page_name.toLowerCase())) {
                        links[i].click();
                        return;
                    }
                }
                var elasped = new Date() - start_time;
                if (elasped < timeout_secs * 1000) {
                    setTimeout(attempt_nav_page, 100, page_name, start_time, timeout_secs);
                } else {
                    alert("Unable to navigate to page '" + page_name + "' after " + timeout_secs + " second(s).");
                }
            }
            window.addEventListener("load", function() {
                attempt_nav_page("%s", new Date(), %d);
            });
        </script>
    """ % (page_name, timeout_secs)
    html(nav_script)

# Display the header for the model catalog with an improved design
st.markdown("<h1 style='text-align: center; font-size: 40px; color: #1e81b0; font-weight: 600;'>Model Catalog 📚</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 16px; color: #6D6875;'>Explore the models available in our catalog. Click on 'View Details' for more information.</p>", unsafe_allow_html=True)

# Create a container for the catalog cards
with st.container():
    # Create a grid layout for the cards
    cols = st.columns(3)  # Adjust the number of columns for the card layout as needed

    # Iterate over each row in the DataFrame and create a card for each project
    for index, row in df.iterrows():
        # Determine the status and its corresponding color
        status, status_color = get_status_style(row.get("stage", "dev"))

        # Display model details as a card with a visually appealing design
        with cols[index % len(cols)]:  # Use modulo to distribute cards evenly across columns
            # Create a card using HTML and custom styling
            st.markdown(
                f"""
                <div style='
                    border: 1px solid #e0e0e0;
                    border-radius: 15px;
                    padding: 20px;
                    margin: 10px;
                    box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.1);
                    background-color: #ffffff;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                ' onmouseover="this.style.transform='scale(1.03)'; this.style.boxShadow='0px 12px 24px rgba(0, 0, 0, 0.15)';" onmouseout="this.style.transform='scale(1.0)'; this.style.boxShadow='0px 8px 16px rgba(0, 0, 0, 0.1)';">
                    <h3 style='text-align: center; color: #007bff;'>{row['project_name']}</h3>
                    <p style='color: #444;'><strong>Algorithm:</strong> {row['algorithm']}</p>
                    <p style='color: #444;'><strong>RMSE:</strong> {row['rmse']:.4f}</p>
                    <p style='color: #444;'><strong>Date of Training:</strong> {row['date_of_training']}</p>
                    <p style='color: white; background-color: {status_color}; border-radius: 10px; padding: 8px; text-align: center; font-weight: bold;'>{status}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Create a View Details button with a professional look
            if st.button(f"View Details - {row['project_name']}", key=f"view_details_{index}"):
                # Store project name in session state for navigation
                st.session_state["selected_model"] = row["project_name"]
                st.session_state["model_details"] = row.to_dict()  # Save the entire row for details page

                # Use the hack to navigate to the Model Details page
                nav_page("Model_Details")

# Check if a project is selected in session state
if "selected_model" in st.session_state:
    selected_project_name = st.session_state["selected_model"]
    st.write(f"Navigating to model details for: {selected_project_name}")
