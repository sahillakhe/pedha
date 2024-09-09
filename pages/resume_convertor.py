import streamlit as st
import os
import uuid
from PyPDF2 import PdfReader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from modules.document_upload import langchain_document_loader
from dotenv import load_dotenv, find_dotenv

# Load API keys from the .env file
load_dotenv(find_dotenv('/Users/sahillakhe/repositories/secrets/keys.env', usecwd=True))
openai_api_key = os.getenv("api_key_openai")

# Ensure the OpenAI API key is available
if not openai_api_key:
    st.error("OpenAI API Key is not set. Please configure it on the homepage.")
    st.stop()

def select_embeddings_model(LLM_service="OpenAI"):
    """Connect to the embeddings API endpoint."""
    if LLM_service == "OpenAI":
        embeddings = OpenAIEmbeddings(
            model='text-embedding-3-large',
            api_key=openai_api_key)
    return embeddings

def create_vectorstore(embeddings, documents):
    """Create a Faiss vector database."""
    vector_store = FAISS.from_documents(documents=documents, embedding=embeddings)
    return vector_store

def validate_pdf(file_path):
    """Validate the uploaded PDF file to ensure it's a valid and readable PDF."""
    try:
        with open(file_path, "rb") as file:
            reader = PdfReader(file)
            if len(reader.pages) == 0:
                return False
        return True
    except Exception as e:
        st.error(f"PDF validation failed: {e}")
        return False

# Streamlit app title
st.title("Batch PDF Embedding Saver")

# Sidebar for Model Selection
st.sidebar.title("Settings")
selected_model = st.sidebar.selectbox("Select Model", ["gpt-3.5-turbo-0125", "gpt-4", "gemini-pro"], index=0)
embedding_service = st.sidebar.selectbox("Select Embedding Service", ["OpenAI"], index=0)
st.sidebar.write(f"Selected Model: {selected_model}")
st.sidebar.write(f"Selected Embedding Service: {embedding_service}")

# Folder Selection
st.header("Select Folder Containing PDFs")
folder_path = st.text_input("Enter the folder path:", "")

# Function to list PDF files in a folder
def list_pdfs(folder_path):
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    return pdf_files

# Display PDF List and Selection
if folder_path:
    if os.path.isdir(folder_path):
        pdf_files = list_pdfs(folder_path)
        if pdf_files:
            st.write("Found the following PDF files:")
            # To keep track of files to delete
            files_to_delete = []
            for i, pdf_file in enumerate(pdf_files):
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.write(pdf_file)
                with col2:
                    if st.button("❌", key=f"delete_{i}"):
                        files_to_delete.append(pdf_file)
            
            # Remove selected files
            for file in files_to_delete:
                pdf_files.remove(file)
                st.warning(f"Removed {file} from the list.")

            if not pdf_files:
                st.info("No PDF files selected.")
        else:
            st.info("No PDF files found in the selected folder.")

        # Save button to store selected PDFs into the vector store
        if pdf_files and st.button("Save Selected Embeddings"):
            all_documents = []
            for pdf_file in pdf_files:
                file_path = os.path.join(folder_path, pdf_file)
                
                # Validate PDF
                if validate_pdf(file_path):
                    # Load documents from each valid PDF
                    documents = langchain_document_loader(file_path)
                    
                    # Assign a unique group ID to each document set (all chunks from the same PDF)
                    group_id = str(uuid.uuid4())  # Generate a unique ID for each PDF

                    # Add group metadata to each chunk
                    for doc in documents:
                        doc.metadata["group_id"] = group_id
                        doc.metadata["source_file"] = pdf_file  # Include source file name for reference

                    all_documents.extend(documents)
                else:
                    st.error(f"{pdf_file} is not a valid PDF.")

            # Save all selected embeddings to vector store
            if all_documents:
                embeddings = select_embeddings_model(LLM_service=embedding_service)
                vector_store = create_vectorstore(embeddings, all_documents)
                vector_store.save_local("/Users/sahillakhe/repositories/db/faiss_index")
                st.success("Embeddings created and stored in the vector database successfully.")
            else:
                st.error("No valid documents were loaded to save.")
    else:
        st.error("The provided path is not a valid directory. Please enter a valid folder path.")