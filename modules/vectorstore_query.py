from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import streamlit as st

def load_vectorstore(load_path, openai_api_key):
    """Load the FAISS vector store with embeddings."""
    try:
        # Initialize the embeddings model using the OpenAI API key
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=openai_api_key)
        
        # Load the FAISS vector store with embeddings
        vector_store = FAISS.load_local(
            load_path, embeddings=embeddings, allow_dangerous_deserialization=True
        )
        st.success("Vector store loaded successfully.")
        return vector_store
    except Exception as e:
        st.error(f"Failed to load the vector store: {e}")
        st.stop()

def query_vectorstore(query, retriever):
    """Retrieve documents using the retriever."""
    try:
        results = retriever.get_relevant_documents(query)
        return results
    except Exception as e:
        st.error(f"Failed to retrieve documents: {e}")
        return []
