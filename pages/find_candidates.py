from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
import streamlit as st
from dotenv import load_dotenv, find_dotenv, set_key
from modules.vectorstore_manager import initialize_vectorstore
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
import os



load_dotenv(find_dotenv('/Users/sahillakhe/repositories/secrets/keys.env', usecwd=True))

# Load API keys
openai_api_key = os.getenv("api_key_openai")

# Ensure the OpenAI API key is available
if not openai_api_key:
    st.error("OpenAI API Key is not set. Please configure it on the homepage.")
    st.stop()

# Initialize OpenAI client and embeddings
client = OpenAI(api_key=openai_api_key)
embeddings = OpenAIEmbeddings(api_key=openai_api_key)

# Sidebar for API key input
st.sidebar.title("API Key Configuration")

# Vector Store Selection
st.sidebar.title("Vector Store Selection")
vector_store_type = st.sidebar.selectbox("Select Vector Store Type", ["Qdrant", "FAISS"], index=0)

# Path for FAISS (if selected)
faiss_path = None
if vector_store_type == "FAISS":
    faiss_path = st.sidebar.text_input("Enter FAISS vector store path:", "/Users/sahillakhe/repositories/db/faiss_index")

qdrant_client = QdrantClient(
    host='localhost',  # Update if different
    port=6333          # Update if different
)

# Define collection name
collection_name = 'resumes'

# Initialize the vector store based on selection
vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name=collection_name,
    embedding=embeddings,
)

if vector_store:
    # Streamlit app title
    st.title("Document Retriever with Vector Store")

    # Choose retrieval method
    retrieval_method = st.radio("Choose retrieval method:", ["Similarity Search", "Job Description Match"])

    if retrieval_method == "Similarity Search":
        # Similarity Search with Score
        query = st.text_input("Enter your query for similarity search:", "Find relevant documents about Python development")
        k = st.slider("Number of results to return", 1, 10, 5)
        
        if st.button("Retrieve Documents (Similarity Search)"):
            if query.strip():
                try:
                    # Generate embedding for the job description using the OpenAIEmbeddings class
                    query_embedding = embeddings.embed_query(query)
                    # Perform a similarity search with scores
                    results_with_scores = vector_store.similarity_search_with_score(query, k=k)

                    # Collect unique group IDs and corresponding filenames
                    # pdf_paths = {}
                    for i, (result, score) in enumerate(results_with_scores, 1):
                        filename = result.metadata.get("filename", "Unknown")

                        st.write(f"Result {i}:")
                        st.write(f"Filename: {filename}")
                        st.write(f"Similarity Score: {score * 100:.4f}")

                    # # Display filenames and similarity scores
                    # if pdf_paths:
                    #     st.write("Matching PDF Files:")
                    #     for filename, score in pdf_paths.items():
                    #         st.write(f"Filename: {filename}, Similarity Score: {score:.4f}")
                    else:
                        st.info("No matching documents found.")
                    
                except Exception as e:
                    st.error(f"Failed to retrieve documents: {e}")

    elif retrieval_method == "Job Description Match":
        # Job Description Matching
        job_description = st.text_area("Enter the job description:", "")
        k = st.slider("Number of candidates to evaluate", 1, 10, 5)

        if st.button("Evaluate Candidates for Job"):
            if job_description.strip():
                try:
                    # Generate embedding for the job description using the OpenAIEmbeddings class
                    job_description_embedding = embeddings.embed_query(job_description)

                    # Perform a similarity search
                    results_with_scores = vector_store.similarity_search_with_score(job_description, k=k)

                    # Track processed candidates by filename to avoid duplicates
                    processed_filenames = set()

                    # Iterate through results and generate explanations
                    for i, (result, score) in enumerate(results_with_scores, 1):
                        filename = result.metadata.get('filename', 'Unknown')

                        # Only process if this filename hasn't been processed yet
                        if filename in processed_filenames:
                            continue
                        processed_filenames.add(filename)

                        candidate_resume_excerpt = result.page_content[:3000]  # Limit to token limits
                        
                        # Construct the prompt for the LLM
                        prompt = f"""
                        You are an expert HR assistant. Given the job description and a candidate's resume, analyze the candidate's suitability for the role.

                        Job Description:
                        {job_description}

                        Candidate Resume:
                        {candidate_resume_excerpt}

                        Provide a brief explanation (2-3 sentences) highlighting why the candidate is a good match.
                        """

                        # Call OpenAI to generate the explanation
                        try:
                            response = client.chat.completions.create(
                                model='gpt-3.5-turbo',  # Use 'gpt-4' if available
                                messages=[
                                    {"role": "system", "content": "You are an assistant that evaluates candidate resumes."},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.7,
                                max_tokens=150
                            )
                            explanation = response.choices[0].message.content.strip()
                        except Exception as e:
                            st.error(f"Error generating explanation for {filename}: {e}")
                            explanation = "No explanation available."

                        # Display result and explanation
                        st.write(f"Result {i}:")
                        st.write(f"Filename: {filename}")
                        st.write(f"Similarity Score: {score * 100:.4f}")
                        st.write(f"Explanation: {explanation}")
                        st.write("-" * 50)
                    
                except Exception as e:
                    st.error(f"Failed to retrieve or evaluate candidates: {e}")
            else:
                st.error("Please enter a job description.")

else:
    st.warning("Vector store not initialized. Please check your configuration.")
