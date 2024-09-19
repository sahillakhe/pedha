from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from modules.cohere_rerank import CohereRerank_retriever
import streamlit as st

def load_vectorstore(load_path, openai_api_key, cohere_api_key=None):
    """Load the FAISS vector store with embeddings."""
    try:
        # Initialize the embeddings model using the OpenAI API key
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=openai_api_key)
        
        # Load the FAISS vector store with embeddings
        vector_store = FAISS.load_local(
            load_path, embeddings=embeddings, allow_dangerous_deserialization=True
        )
        
        # Debug: Print the number of documents loaded in the vector store
        st.success(f"Vector store loaded successfully with {len(vector_store.index_to_docstore_id)} documents.")
        
        # Set up the base retriever
        base_retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 10})

        # If Cohere API key is provided, wrap the retriever with Cohere re-ranking
        if cohere_api_key:
            st.info("Cohere re-ranking enabled.")
            return CohereRerank_retriever(
                base_retriever=base_retriever, 
                cohere_api_key=cohere_api_key,
                cohere_model="rerank-multilingual-v2.0",
                top_n=2
            )
        else:
            return base_retriever
    
    except Exception as e:
        st.error(f"Failed to load the vector store: {e}")
        st.stop()

def query_vectorstore(query, retriever):
    """Retrieve documents using the retriever."""
    try:
        # Retrieve relevant documents
        results = retriever.get_relevant_documents(query)
        
        # Debug: Print number of retrieved documents
        st.write(f"Number of documents retrieved: {len(results)}")
        
        # Debug: Print document metadata and first few characters of content
        for result in results:
            st.write(f"Document Metadata: {result.metadata}")
            st.write(f"Document Content (Snippet): {result.page_content[:200]}")

        return results
    except Exception as e:
        st.error(f"Failed to retrieve documents: {e}")
        return []
