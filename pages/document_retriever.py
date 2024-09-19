import os
import streamlit as st
from dotenv import load_dotenv, find_dotenv, set_key
from modules.vectorstore_query import load_vectorstore, query_vectorstore

# Load existing environment variables from .env file
env_path = find_dotenv('/Users/sahillakhe/repositories/secrets/keys.env', usecwd=True)
load_dotenv(env_path)

# Load API keys
openai_api_key = os.getenv("api_key_openai")
cohere_api_key = os.getenv("api_key_cohere")

# Ensure the OpenAI API key is available
if not openai_api_key:
    st.error("OpenAI API Key is not set. Please configure it on the homepage.")
    st.stop()

# Sidebar for API key input
st.sidebar.title("API Key Configuration")

# Input field for Cohere API key
cohere_api_key_input = st.sidebar.text_input("Cohere API Key", value=cohere_api_key if cohere_api_key else "", type="password")

# Button to save the Cohere API key
if st.sidebar.button("Save Cohere API Key"):
    if cohere_api_key_input:
        set_key(env_path, "api_key_cohere", cohere_api_key_input)
        cohere_api_key = cohere_api_key_input  # Update the variable after saving
        st.sidebar.success("Cohere API key has been saved successfully.")
    else:
        st.sidebar.error("Please enter a valid Cohere API key.")

# Load the FAISS vector store
vector_store = load_vectorstore("/Users/sahillakhe/repositories/db/faiss_index", openai_api_key, cohere_api_key)

# Streamlit app title
st.title("Enhanced Vector Store Retriever")

# Example retrieval query
query = st.text_input("Enter your query:", "Find relevant documents about Python development")

# Button to trigger retrieval
if st.button("Retrieve Documents"):
    try:
        # Retrieve documents using the base retriever first to isolate the issue
        retriever = base_retriever  # Temporarily skip reranking for debugging
        results = query_vectorstore(query, retriever)

        # Collect unique group IDs and corresponding paths
        group_ids = set()
        pdf_paths = {}

        # Iterate over results to collect paths based on group IDs
        for result in results:
            group_id = result.metadata.get("group_id")
            source_file = result.metadata.get("source_file", "Unknown")
            
            if group_id and source_file:
                st.write(f"Found group_id: {group_id}, source_file: {source_file}")
                if group_id not in group_ids:
                    group_ids.add(group_id)
                    pdf_paths[group_id] = source_file  # Store the unique source file path

        # Display unique paths of matching PDFs
        if pdf_paths:
            st.write("Matching PDF Paths:")
            for path in pdf_paths.values():
                st.write(f"- {path}")
        else:
            st.info("No matching PDFs found.")
            
    except Exception as e:
        st.error(f"Failed to retrieve documents: {e}")
