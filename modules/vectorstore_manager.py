# vectorstore_manager.py
import time
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
import streamlit as st
import os

def initialize_vectorstore(store_type, openai_api_key, faiss_path=None, qdrant_config=None):
    """Initialize vector store based on the user selection (FAISS or Qdrant) and store it in session state."""
    embeddings = OpenAIEmbeddings(api_key=openai_api_key)

    if store_type == "FAISS":
        # Load the FAISS vector store
        try:
            vector_store = FAISS.load_local(
                faiss_path, embeddings=embeddings, allow_dangerous_deserialization=True
            )
            st.session_state['store_path'] = faiss_path
            st.session_state['vector_store'] = vector_store  # Store vector store in session state
            st.session_state['store_type'] = "FAISS"  # Track the type of store in session state
            st.success("FAISS vector store loaded successfully.")
            return vector_store
        except Exception as e:
            st.error(f"Failed to load the FAISS vector store: {e}")
            return None

    elif store_type == "Qdrant":
        # Connect to Qdrant instance and set up vector store
        try:
            # Connect to the locally hosted Qdrant instance
            qdrant_client = QdrantClient(
                host='localhost',  # Update if different
                port=6333          # Update if different
            )
            # Define collection parameters
            collection_name = 'resumes'
            vector_size = 1536  # Embedding size for OpenAI embeddings
            distance_metric = Distance.COSINE

            # Check if the collection exists and delete it if it does
            collections = qdrant_client.get_collections().collections
            collection_names = [col.name for col in collections]
            if collection_name in collection_names:
                print(f"::::::::::::::::::::Deleting collection: {collection_name} :::::::::::::::::::::::::::::")
                qdrant_client.delete_collection(collection_name)

            # Create the collection
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance_metric)
            )
            # Create the collection
            vector_store = QdrantVectorStore(client=qdrant_client, collection_name=collection_name, embedding=embeddings)
            st.session_state['vector_store'] = vector_store  # Store vector store in session state
            st.session_state['store_type'] = "Qdrant"  # Track the type of store in session state
            st.success("Qdrant vector store initialized successfully.")
            return vector_store

        except Exception as e:
            st.error(f"Failed to initialize the Qdrant vector store: {e}")
            return None

    else:
        st.error(f"Unsupported vector store: {store_type}")
        return None
def save_to_vectorstore(documents):
    """Save embeddings to the active vector store in session state."""
    if 'vector_store' not in st.session_state or 'store_type' not in st.session_state:
        st.error("No vector store is initialized. Please initialize a vector store first.")
        return

    vector_store = st.session_state['vector_store']
    store_type = st.session_state['store_type']
    print(type(store_type))
    # Save to FAISS vector store
    if store_type == "FAISS":
        try:
            # Assuming embeddings have already been generated for documents
            vector_store.add_texts(
                texts=[documents['page_content']],
                metadatas=[documents['metadata']]
            )
            vector_store.save_local(st.session_state['store_path'])
            st.success("Document saved to FAISS vector store successfully.")
        except Exception as e:
            st.error(f"Failed to save documents to FAISS vector store: {e}")

    # Save to Qdrant vector store
    elif store_type == "Qdrant":
        try:
            vector_store.add_texts(
            texts=[documents['page_content']],
            metadatas=[documents['metadata']],
  
            )
            # Respect OpenAI's rate limits
            time.sleep(1) 
  
            st.success(f"{documents['metadata']['filename']} saved to Qdrant vector store successfully.")
        except Exception as e:
            st.error(f"Failed to save documents to Qdrant vector store: {e}")