import os
import glob
import json
import time
import openai
from openai import OpenAI


from pdfminer.high_level import extract_text
from docx import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from dotenv import load_dotenv

# Load environment variables from keys.env
load_dotenv('/Users/sahillakhe/repositories/secrets/keys.env')

# Set OpenAI API key
OPENAI_API_KEY = os.getenv('api_key_openai')

# Verify that the API key is loaded
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Please set api_key_openai in keys.env file.")


client = OpenAI(api_key=OPENAI_API_KEY)
# Function to extract text from PDF files
def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    return text

# Function to extract text from DOCX files
def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text

# Function to parse resume text using OpenAI API
def parse_resume_with_openai(text):
    # Define the schema as a string to include in the prompt
    schema = """
    {
      "personalInformation": {
        "first_name": "string",
        "last_name": "string",
        "job_title": "string",
        "birth_date": "yyyy-mm-dd"
      },
      "contact": {
        "phone": "string",
        "email": "string",
        "github": "string",
        "linkedin": "string"
      },
      "about": {
        "summary": "string",
        "skill_tags": [
          "string", "string"
        ]
      },
      "work_experience": [
        {
          "company": "string",
          "location": {"country": "string", "city": "string"},
          "position": "string",
          "start_date": "string",
          "end_date": "string",
          "achievements": ["string"],
          "role_description": "string",
          "tools": ["string"]
        }
      ],
      "education": [
        {
          "institution": "string",
          "end_date": "yyyy-mm-dd",
          "location": {"country": "string", "city": "string"},
          "program": "string"
        }
      ],
      "expertise": {
        "experience": [
          {
            "name": "string",
            "proficiency": "string"
          }
        ],
        "programming_language": [
          {
            "name": "string",
            "proficiency": "string"
          }
        ],
        "development_tools": [
          {
            "name": "string",
            "proficiency": "string"
          }
        ]
      },
      "courses": [{"institution": "string", "end_date": "yyyy-mm-dd", "title": "string"}],
      "languages": [{"name": "string", "proficiency": "string"}]
    }
    """

    # Craft the prompt
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

    # Call the OpenAI API
    try:
        response = client.chat.completions.create(model='gpt-3.5-turbo',  # Use 'gpt-4' if you have access
        messages=[
            {"role": "system", "content": "You are an assistant that parses resumes into structured JSON data."},
            {"role": "user", "content": prompt}
        ],
        temperature=0 ) # Set temperature to 0 for deterministic output)
        # Extract the assistant's reply
        reply = response.choices[0].message.content.strip()
        # Load the reply as JSON
        structured_data = json.loads(reply)
        return structured_data
    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        print(f"Assistant's reply: {reply}")
        return None
    finally:
        print("Completed OpenAI API call.")

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

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
    qdrant_client.delete_collection(collection_name)

# Create the collection
qdrant_client.create_collection(
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
        print(f"Skipping unsupported file type: {resume_file}")
        continue  # Skip unsupported file types

    # Parse the resume text into structured data using OpenAI API
    structured_data = parse_resume_with_openai(text)
    if not structured_data:
        print(f"Failed to parse resume: {resume_file}")
        continue

    # Add the filename to the metadata
    structured_data['filename'] = os.path.basename(resume_file)

    # Create a document with the text and metadata
    doc = {
        'page_content': text,
        'metadata': structured_data
    }

    # Add the document to the Qdrant vector store
    vectorstore.add_texts(
        texts=[doc['page_content']],
        metadatas=[doc['metadata']]
    )

    # Respect OpenAI's rate limits
    time.sleep(1)  # Adjust sleep time as needed

print("Resumes have been successfully processed and stored in Qdrant.")