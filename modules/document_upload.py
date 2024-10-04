import os
import json
import time
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

        reply = response.choices[0].message.content.strip()
        structured_data = json.loads(reply)
        return structured_data

    except openai.OpenAIError as e:
        st.error(f"OpenAI API error: {e}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"JSON decoding error: {e}")
        return None
    finally:
        time.sleep(1)  # Respect OpenAI rate limits

# Function to create embeddings for the extracted text
def generate_embeddings(text):
    """Generates embeddings for a given text using OpenAI API"""
    try:
        embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        return embeddings.embed_query(text)
    except Exception as e:
        st.error(f"Failed to generate embeddings: {e}")
        return None

# Unified function to process documents and return parsed data and embeddings
def process_document(doc):
    """Process a single document, extract text, parse resumes, and generate embeddings."""

    # Extract text from PDF or DOCX
    if doc.endswith('.pdf'):
        text = extract_text_from_pdf(doc)
    elif doc.endswith('.docx'):
        text = extract_text_from_docx(doc)
    else:
        st.error(f"Unsupported file type: {doc}")


    # If text was extracted successfully, parse the resume and generate embeddings
    if text:
        # Parse the resume text into structured data using OpenAI API
        structured_data = parse_resume_with_openai(text)
        if not structured_data:
            print(f"Failed to parse resume: {doc}")

        # Add the filename to the metadata
        structured_data['filename'] = os.path.basename(doc)

        # Create a document with the text and metadata
        # vector_document = vectorDocument(
        #     page_content=text,
        #     metadata=structured_data
        # )
        doc = {
        'page_content': structured_data,
        'metadata': structured_data['filename']
        }
        print(doc)
        return doc
    else:
        st.error(f"Failed to parse resume: {doc}")
        return None


