import streamlit as st
from modules.llm_functions import load_api_keys, save_api_key

# Sidebar for configuration
st.sidebar.title("Configuration")

# Input field for .env file path
env_path_input = st.sidebar.text_input(
    "Path to folder for secret keys",
    value="",
    help="You will need to enter your OpenAI keys in the next field. Enter the path for a folder of your choosing where to save"
)

# Load API keys using the utility function
openai_api_key = load_api_keys(env_path=env_path_input)

# Set up the Streamlit app layout
st.title("Consultancy Firm Hiring Tool")
st.subheader("Streamline your hiring and matching process with AI-powered automation")

st.write("""
Our tool is designed to streamline the hiring and matching process for consultancy firms by automating the management of resumes and job descriptions. It provides the following capabilities:

1. Resume Conversion and Database Storage
2. Job Description and Advertisement Management
3. Job Matching for Candidates
4. Candidate Matching for Jobs

Use the sidebar to navigate between different functionalities.
""")

st.header("AI-Powered and Secure")
st.write("""
Our tool utilizes AI models that are locally hosted within the company premises. This ensures that all processes, including resume extraction, conversion, and job matching, are conducted securely on-site. No data or information is sent outside the company, providing complete control and confidentiality over sensitive information.
""")

# Sidebar for API key inputs
st.sidebar.title("API Key Configuration")

# Input fields for API keys
openai_api_key_input = st.sidebar.text_input(
    "OpenAI API Key",
    value=openai_api_key if openai_api_key else "",
    type="password"
)

# Save button to update .env file
if st.sidebar.button("Save API Keys"):
    if openai_api_key_input:
        save_api_key("api_key_openai", openai_api_key_input, env_path=env_path_input)
    st.sidebar.success("API keys have been saved successfully.")
