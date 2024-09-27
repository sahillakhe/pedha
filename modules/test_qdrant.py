import os
import sys
import argparse
import json
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import Qdrant
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv

# Load environment variables from keys.env
load_dotenv('/Users/sahillakhe/repositories/secrets/keys.env')

# Set OpenAI API key
OPENAI_API_KEY = os.getenv('api_key_openai')

# Verify that the API key is loaded
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Please set api_key_openai in keys.env file.")

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
vectorstore = QdrantVectorStore(
    client=qdrant_client,
    collection_name=collection_name,
    embedding=embeddings,
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

# Perform a similarity search with scores
results = vectorstore.similarity_search_with_score(query=search_query, k=args.k)

# Display the results
for i, (doc, score) in enumerate(results, 1):
    filename = doc.metadata.get('filename', 'Unknown')
    similarity = score * 100  # Convert distance to similarity if using cosine distance
    print(f"Result {i}:")
    print(f"Filename: {filename}")
    print(f"Similarity Score: {similarity:.4f}%")
    print("-" * 50)