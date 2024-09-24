import os
import glob
import re
import json
from pdfminer.high_level import extract_text
from docx import Document
import spacy
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document as LCDocument
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from dotenv import load_dotenv

# Load environment variables from keys.env
load_dotenv('/Users/sahillakhe/repositories/secrets/keys.env')

# Set OpenAI API key
OPENAI_API_KEY = os.getenv('api_key_openai')

# Verify that the API key is loaded
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in keys.env file.")

# Load spaCy model for NLP tasks
nlp = spacy.load('en_core_web_sm')

# Function to extract text from PDF files
def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    return text

# Function to extract text from DOCX files
def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text

# Function to parse resume text into structured JSON format
def parse_resume(text):
    # Initialize the structured data dictionary according to the schema
    structured_data = {
        "personalInformation": {
            "first_name": "",
            "last_name": "",
            "job_title": "",
            "birth_date": ""
        },
        "contact": {
            "phone": "",
            "email": "",
            "github": "",
            "linkedin": ""
        },
        "about": {
            "summary": "",
            "skill_tags": []
        },
        "work_experience": [],
        "education": [],
        "expertise": {
            "experience": [],
            "programming_language": [],
            "development_tools": []
        },
        "courses": [],
        "languages": []
    }

    doc = nlp(text)

    # Extract names
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            names = ent.text.split()
            if len(names) >= 2:
                structured_data['personalInformation']['first_name'] = names[0]
                structured_data['personalInformation']['last_name'] = ' '.join(names[1:])
            else:
                structured_data['personalInformation']['first_name'] = names[0]
            break  # Assuming the first PERSON entity is the candidate's name

    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    if email_match:
        structured_data['contact']['email'] = email_match.group(0)

    # Extract phone number
    phone_match = re.search(r'(\+\d{1,3}\s)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{4}', text)
    if phone_match:
        structured_data['contact']['phone'] = phone_match.group(0)

    # Extract LinkedIn URL
    linkedin_match = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[\w\-/]+', text)
    if linkedin_match:
        structured_data['contact']['linkedin'] = linkedin_match.group(0)

    # Extract GitHub URL
    github_match = re.search(r'(https?://)?(www\.)?github\.com/[\w\-/]+', text)
    if github_match:
        structured_data['contact']['github'] = github_match.group(0)

    # Extract skills (assuming they are listed under 'Skills' section)
    skill_tags = []
    skills_section = re.findall(r'(Skills|Technical Skills|Expertise)\s*[:\-–]?\s*((?:\w+(?:,|\s))+)', text, re.IGNORECASE)
    if skills_section:
        skills_text = skills_section[0][1]
        skill_tags = [skill.strip() for skill in re.split(r',|\n', skills_text) if skill.strip()]
        structured_data['about']['skill_tags'] = skill_tags

    # Extract summary (assuming it's the first paragraph)
    summary = text.strip().split('\n')[0]
    structured_data['about']['summary'] = summary

    # Additional parsing can be added here for work_experience, education, etc.

    return structured_data

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Connect to the locally hosted Qdrant instance
qdrant_client = QdrantClient(
    host='localhost',  # Change if your Qdrant host is different
    port=6333
)

# Define collection parameters
collection_name = 'resumes'
vector_size = 1536  # Embedding size for OpenAI embeddings (e.g., 'text-embedding-ada-002')
distance_metric = Distance.COSINE

# Create or recreate the collection in Qdrant
qdrant_client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=vector_size, distance=distance_metric)
)

# Initialize the Qdrant vector store with LangChain
vectorstore = Qdrant(
    client=qdrant_client,
    collection_name=collection_name,
    embeddings=embeddings,
)

# Directory containing the resume files
resume_dir = '/Users/sahillakhe/repositories/scionova/resume_database/input'  # Replace with your directory path
resume_files = glob.glob(os.path.join(resume_dir, '*'))

# Process each resume file
for resume_file in resume_files:
    file_extension = os.path.splitext(resume_file)[1].lower()
    if file_extension == '.pdf':
        text = extract_text_from_pdf(resume_file)
    elif file_extension == '.docx':
        text = extract_text_from_docx(resume_file)
    else:
        continue  # Skip unsupported file types

    # Parse the resume text into structured data
    structured_data = parse_resume(text)

    # Create a LangChain Document with the text and metadata
    doc = LCDocument(
        page_content=text,
        metadata=structured_data
    )

    # Add the document to the Qdrant vector store
    vectorstore.add_documents([doc])

print("Resumes have been successfully processed and stored in Qdrant.")