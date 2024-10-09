import streamlit as st
import os
import uuid
from modules.document_upload import process_document, extract_text_from_pdf, parse_resume_with_openai
from modules.vectorstore_manager import initialize_vectorstore, save_to_vectorstore
from uuid import uuid4
from dotenv import load_dotenv, find_dotenv

# Load API keys from the .env file
load_dotenv(find_dotenv('/Users/sahillakhe/repositories/secrets/keys.env', usecwd=True))
openai_api_key = os.getenv("api_key_openai")

# Ensure the OpenAI API key is available
if not openai_api_key:
    st.error("OpenAI API Key is not set. Please configure it on the homepage.")
    st.stop()

# Streamlit app title
st.title("Batch PDF Embedding Saver")

# Sidebar for Model Selection
st.sidebar.title("Settings")
selected_model = st.sidebar.selectbox("Select Model", ["gpt-3.5-turbo-0125", "gpt-4", "gemini-pro"], index=0)
embedding_service = st.sidebar.selectbox("Select Embedding Service", ["OpenAI"], index=0)

# Vector store selection (FAISS or Qdrant)
vector_store_type = st.sidebar.selectbox("Select Vector Store", [ "Qdrant", "FAISS"], index=0)

# Set FAISS path and Qdrant configuration (Modify according to your setup)
faiss_path = "/Users/sahillakhe/repositories/db/faiss_index"
# qdrant_config = {
#     "host": "localhost",
#     "port": 6333,
#     "collection_name": "resumes"
# }

# Folder Selection
st.header("Select Folder Containing Resumes")
folder_path = st.text_input("Enter the folder path:", "")

# Function to list PDF files in a folder
def list_documents(folder_path):
    supported_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf') or  f.endswith('.docx')]
    return supported_files

# Display PDF List and Selection
if folder_path:
    if os.path.isdir(folder_path):
        supported_files = list_documents(folder_path)
        
        if supported_files:
            st.write(f" {len(supported_files)} resumes found in the selected folder") 

        else:
            st.info("No supported files found in the selected folder.")
        
        vector_store = initialize_vectorstore(
            store_type=vector_store_type,
            openai_api_key=openai_api_key,
            faiss_path=faiss_path,
        )
        uuids = [str(uuid4()) for _ in range(len(supported_files))]
        progress_text = "Uploading Resumes to database ..." 
        my_bar = st.progress(0, text=progress_text)

        number_of_files = len(supported_files)
        my_bar.progress(0, text=progress_text)
        for file in supported_files:
            file_name = os.path.basename(file)

            print(progress_text)
            file_path = os.path.join(folder_path, file)
            vectorDocument = process_document(file_path)
            # extracted_file = extract_text_from_pdf(file_path)
            # structured_data = parse_resume_with_openai(extracted_file)
            
            # if not structured_data:
            #     print(f"Failed to parse resume: {file}")
            #     continue
            
            # # Add the filename to the metadata
            # structured_data['filename'] = file_name
            # # Create a document with the text and metadata
            # vector_file = {
            #     'page_content': extracted_file,
            #     'metadata': structured_data,
            # }
            save_to_vectorstore(vectorDocument)
            progress_text = f"Processing {file_name} ..."
            my_bar.empty()
            my_bar.progress((supported_files.index(file) + 1) / number_of_files, text=progress_text)
            if(supported_files.index(file) + 1 == number_of_files):
                my_bar.empty()
                st.write("All resumes uploaded successfully")
        


    else:
        st.error("The provided path is not a valid directory. Please enter a valid folder path.")