import streamlit
import os

streamlit_path = os.path.dirname(streamlit.__file__)
streamlit_static_path = os.path.join(streamlit_path, 'static')

print(f"Streamlit package path: {streamlit_path}")
print(f"Streamlit static assets path: {streamlit_static_path}")
print(f"Static assets directory exists: {os.path.exists(streamlit_static_path)}")
