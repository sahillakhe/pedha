# test_qdrant.py
import os
import sys
import argparse
import json
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from openai import OpenAI



# Load environment variables from keys.env
load_dotenv('/Users/sahillakhe/repositories/secrets/keys.env')

# Set OpenAI API key
OPENAI_API_KEY = os.getenv('api_key_openai')

# Verify that the API key is loaded
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Please set api_key_openai in keys.env file.")


client = OpenAI(api_key=OPENAI_API_KEY)
# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Connect to the locally hosted Qdrant instance
qdrant_client = QdrantClient(
    host='localhost',  # Update if different
    port=6333          # Update if different
)

# Define collection name
collection_name = 'resumes'

# Initialize the Qdrant vector store with LangChain
vectorstore = Qdrant(
    client=qdrant_client,
    collection_name=collection_name,
    embeddings=embeddings,
)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Search resumes using a job description.')
parser.add_argument('--job-description-file', type=str, help='Path to the job description text file.')
parser.add_argument('-k', type=int, default=5, help='Number of results to return')
args = parser.parse_args()

if not args.job_description_file:
    print("Please provide a job description file using --job-description-file.")
    sys.exit(1)

# Read the job description from the file
with open(args.job_description_file, 'r') as f:
    job_description = f.read()

if not job_description.strip():
    print("Job description is empty.")
    sys.exit(1)

# Generate embedding for the job description
job_description_embedding = embeddings.embed_query(job_description)

# Perform a similarity search with scores
results_with_scores = vectorstore.similarity_search_with_score_by_vector(
    job_description_embedding, k=args.k
)

print("Top candidates for the job description:")
for i, (doc, score) in enumerate(results_with_scores, 1):
    filename = doc.metadata.get('filename', 'Unknown')
    similarity = score  # Convert cosine distance to similarity
    # Limit the resume content to avoid exceeding token limits
    candidate_resume_excerpt = doc.page_content[:2000]

    # Construct the prompt for the LLM
    prompt = f"""
You are an expert HR assistant. Given the job description and a candidate's resume, analyze the candidate's suitability for the role.

Job Description:
{job_description}

Candidate Resume:
{candidate_resume_excerpt}

Provide a brief explanation (2-3 sentences) highlighting why the candidate is a good match.

Output:
"""

    try:
        response = client.chat.completions.create(model='gpt-3.5-turbo',  # Use 'gpt-4' if available
        messages=[
            {"role": "system", "content": "You are an assistant that evaluates candidate resumes."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=150)
        explanation = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating explanation for candidate {filename}: {e}")
        explanation = "No explanation available."

    print(f"Result {i}:")
    print(f"Filename: {filename}")
    print(f"Similarity Score: {similarity:.4f}")
    print(f"Explanation: {explanation}")
    print("-" * 50)