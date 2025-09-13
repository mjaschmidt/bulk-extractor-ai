# app.py
import streamlit as st
import requests

# --- Page Configuration ---
# This must be the first Streamlit command in your script.
st.set_page_config(
    page_title="Bulk Extractor AI",
    page_icon="🤖",
    layout="centered"
)

# --- Backend API URL ---
# API_URL = "http://localhost:8000/extract"  # Development (local FastAPI server)
API_URL = "https://bulk-extractor-ai-backend.onrender.com/extract/"

# --- UI Components ---

# 1. Title and Introduction
st.title("🤖 Bulk Extractor AI")
st.markdown(
    "Welcome! This tool uses AI to extract structured information from your files. "
    "Just upload your files, describe what you need, and let the AI do the work."
)
st.divider()

# 2. Sidebar for Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Input for the user's API key
    api_key = st.text_input(
        "Enter your Gemini API Key", 
        type="password",
        help="Get your free key from Google AI Studio."
    )
    
    # Radio buttons for selecting the output method
    output_method = st.radio(
        "Select Output Method",
        options=["one_per_relevant_file", "one_per_file", "single_file"],
        captions=[
            "Creates a JSON file only if relevant data is found.",
            "Creates a JSON file for every input file.",
            "Combines all results into a single JSON file."
        ],
        index=0 # Default selection
    )
    st.info("The API and your files are not stored. This is a 'Bring Your Own Key' service.")

# 3. Main Interaction Area
st.header("1. Upload Your Files")
uploaded_files = st.file_uploader(
    "Choose your .eml files",
    accept_multiple_files=True,
    type=['eml']
)

st.header("2. Describe Your Goal")
user_goal = st.text_area(
    "In simple terms, what information do you want to extract?",
    placeholder="e.g., 'Extract all grocery items with their name, quantity, and price, and also find the delivery address.'"
)

st.divider()

# 4. The "Run" Button and Backend Logic
if st.button("✨ Run Extraction", type="primary"):
    # --- 1. Input Validation ---
    if not api_key:
        st.warning("Please enter your Gemini API key in the sidebar.")
    elif not uploaded_files:
        st.warning("Please upload at least one .eml file.")
    elif not user_goal:
        st.warning("Please describe your extraction goal.")
    else:
        # --- 2. Prepare for API Call ---
        # Show a spinner to indicate that processing is happening.
        with st.spinner("AI is processing your files... Please wait."):
            
            # Prepare the form data
            form_data = {
                'api_key': (None, api_key),
                'user_goal': (None, user_goal),
                'output_method': (None, output_method),
            }
            
            # Prepare the files for multipart/form-data upload
            files_to_upload = []
            for uploaded_file in uploaded_files:
                # Create a tuple for each file: (fieldname, (filename, file-like-object, content_type))
                files_to_upload.append(
                    ('files', (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type))
                )

            # --- 3. Make the API Request ---
            try:
                response = requests.post(API_URL, data=form_data, files=files_to_upload)

                # --- 4. Handle the Response ---
                if response.status_code == 200:
                    st.success("Extraction complete! Your results are ready for download.")
                    
                    # Create a download button for the received zip file
                    st.download_button(
                        label="📥 Download Results (.zip)",
                        data=response.content,
                        file_name="extraction_results.zip",
                        mime="application/zip"
                    )
                else:
                    # Display an error message if the API call failed
                    error_details = response.json().get('detail', 'An unknown error occurred.')
                    st.error(f"An error occurred: {error_details} (Status Code: {response.status_code})")

            except requests.exceptions.ConnectionError:
                st.error("Connection Error: Could not connect to the backend service. Is the FastAPI server running?")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")