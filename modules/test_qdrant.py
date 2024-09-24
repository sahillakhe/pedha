import os
import sys
import argparse
import json
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables from keys.env
load_dotenv('/Users/sahillakhe/repositories/secrets/keys.env')

# Set OpenAI API key
OPENAI_API_KEY = os.getenv('api_key_openai')

# Verify that the API key is loaded
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in keys.env file.")

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
parser = argparse.ArgumentParser(description='Search resumes using a query.')
parser.add_argument('query', nargs='+', help='The search query')
parser.add_argument('-k', type=int, default=5, help='Number of results to return')
args = parser.parse_args()

# Combine query words into a single string
search_query = ' '.join(args.query)

if not search_query:
    print("Please provide a search query.")
    sys.exit(1)

# Perform a similarity search
results = vectorstore.similarity_search(query=search_query, k=args.k)

# Display the results
for i, result in enumerate(results, 1):
    print(f"Result {i}:")
    print(f"Content: {result.page_content[:200]}...")  # Print first 200 characters
    print(f"Metadata: {json.dumps(result.metadata, indent=2)}")
    print("-" * 50)