import streamlit as st
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv, find_dotenv, set_key
import ftfy  # Import ftfy for text cleaning
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank

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

# Initialize the embeddings model using the OpenAI API key
embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=openai_api_key)

# Load the existing FAISS vector store from disk
load_path = "/Users/sahillakhe/repositories/db/faiss_index"

try:
    # Load the FAISS vector store with embeddings
    vector_store = FAISS.load_local(
        load_path, embeddings=embeddings, allow_dangerous_deserialization=True
    )
    st.success("Vector store loaded successfully.")
except Exception as e:
    st.error(f"Failed to load the vector store: {e}")
    st.stop()

# Function to create Cohere Rerank-based retriever
def CohereRerank_retriever(base_retriever, cohere_api_key, cohere_model="rerank-multilingual-v2.0", top_n=2):
    """Build a ContextualCompressionRetriever using Cohere Rerank endpoint to reorder the results based on relevance."""
    compressor = CohereRerank(
        cohere_api_key=cohere_api_key, 
        model=cohere_model, 
        top_n=top_n
    )
    retriever_Cohere = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever
    )
    return retriever_Cohere

# Initialize the base retriever from the vector store
base_retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 10})

# Create the enhanced retriever using Cohere's re-rank model, only if the key is available
if cohere_api_key:
    enhanced_retriever = CohereRerank_retriever(
        base_retriever=base_retriever, 
        cohere_api_key=cohere_api_key,
        cohere_model="rerank-multilingual-v2.0",
        top_n=2
    )
else:
    st.error("Cohere API Key is not set. Please configure it in the sidebar.")

# Streamlit app title
st.title("Enhanced Vector Store Retriever with Cohere Rerank")

# Example retrieval query
query = st.text_input("Enter your query:", "Find relevant documents about Python development")

# Button to trigger retrieval
if st.button("Retrieve Documents") and cohere_api_key:
    try:
        # Retrieve documents using the enhanced retriever
        results = enhanced_retriever.get_relevant_documents(query)

        # Collect unique group IDs and corresponding paths
        group_ids = set()
        pdf_paths = {}
        
        # Iterate over results to collect paths based on group IDs
        for result in results:
            group_id = result.metadata.get("group_id")
            source_file = result.metadata.get("source_file", "Unknown")
            
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