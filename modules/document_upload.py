# document_upload.py

from langchain_community.document_loaders import PDFMinerLoader
import streamlit as st

def langchain_document_loader(file_path):
    """Load and split a PDF file in Langchain.
    Parameters:
        - file_path (str): path of the file.
    Output:
        - documents: list of Langchain Documents.
    """
    documents = []

    if file_path.endswith(".pdf"):
        # Load and split the PDF document
        loader = PDFMinerLoader(file_path=file_path)
        documents = loader.load_and_split()

        # Update the metadata: add document number
        for i in range(len(documents)):
            documents[i].metadata = {
                "source": documents[i].metadata["source"],
                "doc_number": i,
            }

        st.success(f"Successfully loaded {len(documents)} document(s) from the PDF.")
    else:
        st.error("You can only upload .pdf files!")

    return documents