import streamlit.web.bootstrap
import sys
import os

if __name__ == '__main__':
    # Get the absolute path to your app.py
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    # Pass any command-line arguments to Streamlit
    streamlit.web.bootstrap.run(script_path, '', sys.argv[1:], {})
