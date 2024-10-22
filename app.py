import sys
import os


# Rest of your imports and code
import streamlit as st
from modules.llm_functions import load_api_keys, save_api_key

# Set STREAMLIT_CONFIG_DIR before importing streamlit
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

os.environ['STREAMLIT_CONFIG_DIR'] = resource_path('.streamlit')

import streamlit  # Import streamlit after setting STREAMLIT_CONFIG_DIR

print(f"Development mode: {st.config.get_option('global.developmentMode')}")


static_assets_path = os.path.join(os.path.dirname(streamlit.__file__), 'static')
print(f"Static assets path: {static_assets_path}")
print(f"Static assets exist: {os.path.exists(static_assets_path)}")


def main():
    # Load API keys using the utility function
    openai_api_key, google_api_key, cohere_api_key = load_api_keys()

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
    openai_api_key_input = st.sidebar.text_input("OpenAI API Key", value=openai_api_key, type="password")
    google_api_key_input = st.sidebar.text_input("Google API Key", value=google_api_key, type="password")
    cohere_api_key_input = st.sidebar.text_input("Cohere API Key", value=cohere_api_key, type="password")

    # Save button to update .env file
    if st.sidebar.button("Save API Keys"):
        if openai_api_key_input:
            save_api_key("api_key_openai", openai_api_key_input)
        if google_api_key_input:
            save_api_key("api_key_google", google_api_key_input)
        if cohere_api_key_input:
            save_api_key("api_key_cohere", cohere_api_key_input)
        st.sidebar.success("API keys have been saved successfully.")




# If developmentMode is still True, you can force it to False
# st.set_option('global.developmentMode', False)
if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        # The app is being run as a frozen executable
        import streamlit.web.bootstrap

        # Set the STREAMLIT_CONFIG_DIR environment variable
        base_path = os.path.dirname(sys.executable)
        os.environ['STREAMLIT_CONFIG_DIR'] = resource_path('.streamlit')

        # Path to 'app.py' within the 'dist' directory
        script_path = os.path.join(base_path, '_internal','app.py', 'app.py')
        print(f"Script path:::: {script_path}")
        # Run the Streamlit app
        streamlit.web.bootstrap.run(
            script_path,  # Path to the script file
            '',           # 'is_hello' parameter (empty string or False)
            sys.argv[1:], # Command-line arguments
            {}            # Flag options
        )
        sys.exit(0)
    else:
        # Running in development mode
        main()