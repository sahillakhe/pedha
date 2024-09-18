from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank

def CohereRerank_retriever(base_retriever, cohere_api_key, cohere_model="rerank-multilingual-v2.0", top_n=2):
    """Build a ContextualCompressionRetriever using Cohere Rerank endpoint to reorder the results based on relevance."""
    compressor = CohereRerank(
        cohere_api_key=cohere_api_key, 
        model=cohere_model, 
        top_n=top_n
    )
    retriever_Cohere = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever
    )
    return retriever_Cohere
