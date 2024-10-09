import os
import json
import time
from tokenize import String
from openai import OpenAI


import openai
from pdfminer.high_level import extract_text
from docx import Document
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from modules.global_variables import schema
from langchain_core.documents import Document as vectorDocument
import streamlit as st


# Load environment variables from keys.env
load_dotenv('/Users/sahillakhe/repositories/secrets/keys.env')

# Set OpenAI API key
OPENAI_API_KEY = os.getenv('api_key_openai')

# Verify that the API key is loaded
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Please set api_key_openai in keys.env file.")

client = OpenAI(api_key=OPENAI_API_KEY)
# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        st.error(f"Failed to extract text from PDF: {e}")
        return None

# Function to extract text from DOCX
def extract_text_from_docx(docx_path):
    try:
        doc = Document(docx_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        st.error(f"Failed to extract text from DOCX: {e}")
        return None

# Function to parse resume using OpenAI and convert it to JSON format
def parse_resume_with_openai(text):
    prompt = f"""
You are a professional resume parser. Your task is to extract information from the provided resume text and output a JSON object following the given schema.
First, clean and preprocess the text to ensure it is properly formatted and makes contextual sense.
Then, extract the relevant information and populate the JSON object accordingly. If certain fields are missing in the resume, you can leave them empty or as null.
Ensure that dates are in the format "yyyy-mm-dd" and all strings are properly escaped.
Please make sure to return only the JSON; it cannot have any characters before or after the JSON. This is very important. Also, please remove any code blocks like ```json at the beginning and ``` at the end.

Schema:
{schema}

Resume Text:
\"\"\"
{text}
\"\"\"

Output:
"""

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that parses resumes into structured JSON data."},
            {"role": "user", "content": prompt}
        ],
        temperature=0)

        structured_data_in_string = response.choices[0].message.content.strip()
        # structured_data_in_string = json.loads(reply)
        return structured_data_in_string

    except openai.OpenAIError as e:
        st.error(f"OpenAI API error: {e}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"JSON decoding error: {e}")
        return None
    finally:
        time.sleep(1)  # Respect OpenAI rate limits

# Function to create embeddings for the extracted text
# def generate_embeddings(text):
#     """Generates embeddings for a given text using OpenAI API"""
#     try:
#         embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
#         return embeddings.embed_query(text)
#     except Exception as e:
#         st.error(f"Failed to generate embeddings: {e}")
#         return None

# Unified function to process documents and return parsed data and embeddings
def process_document(file_path):
    """Process a single document, extract text, parse resumes, and generate embeddings."""

    # Extract text from PDF or DOCX
    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        st.error(f"Unsupported file type: {file_path}")


    # If text was extracted successfully, parse the resume and generate embeddings
    if text:
        # Parse the resume text into structured data using OpenAI API
        structured_data_in_string = parse_resume_with_openai(text)
        if not structured_data_in_string:
            print(f"Failed to parse resume: {file_path}")

        # Add the filename to the metadata
        metadata = {'filename': file_path}

        vectorDocument = {
        'page_content': structured_data_in_string,
        'metadata': metadata
        }
        return vectorDocument
    else:
        st.error(f"Failed to parse resume: {file_path}")
        return None


