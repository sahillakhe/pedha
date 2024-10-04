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
            st.write("Found the following PDF files:")
            # To keep track of files to delete
            files_to_delete = []
            for i, file in enumerate(supported_files):
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.success(file)
                # with col2:
                #     if st.button("❌", key=f"delete_{i}"):

                #         files_to_delete.append(file)
            
            # Remove selected files
            # for file in files_to_delete:
            #     supported_files.remove(file)
            #     st.success(f"Removed {file} from the list.")

        
        else:
            st.info("No supported files found in the selected folder.")
        
        vector_store = initialize_vectorstore(
            store_type=vector_store_type,
            openai_api_key=openai_api_key,
            faiss_path=faiss_path,
        )
        uuids = [str(uuid4()) for _ in range(len(supported_files))]
        i=0
        for file in supported_files:
            if(i > 2):
                break
            file_path = os.path.join(folder_path, file)
            extracted_file = extract_text_from_pdf(file_path)
            structured_data = parse_resume_with_openai(extracted_file)
            
            if not structured_data:
                print(f"Failed to parse resume: {file}")
                continue

            # Add the filename to the metadata
            structured_data['filename'] = os.path.basename(file)
            print(type(structured_data    ))
            # Create a document with the text and metadata
            vector_file = {
                'page_content': extracted_file,
                'metadata': structured_data,
            }
            st.write(vector_file)
            save_to_vectorstore(vector_file)
            i+=1
            st.divider()
        

        # vector_store = initialize_vectorstore(
        #     store_type=vector_store_type,
        #     openai_api_key=openai_api_key,
        #     faiss_path=faiss_path,
        #     qdrant_config=qdrant_config
        # )
        # # Save button to store selected PDFs into the vector store
        # if supported_files and st.button("Save Selected Embeddings"):

        #     uuids = [str(uuid4()) for _ in range(len(supported_files))]
        #     for doc in supported_files:
        #         file_path = os.path.join(folder_path, doc)
        #         st.write(file_path)
        #     # Process documents one by one
        #         vector_document = process_document(file_path)
        #         if vector_store and vector_document:
        #             save_to_vectorstore(vector_document,uuid)
                    
                
        #         else:
        #             st.error(f"Failed to initialize the {vector_store_type} vector store.")
    else:
        st.error("The provided path is not a valid directory. Please enter a valid folder path.")