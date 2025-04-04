import os
import numpy as np
import ollama
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import uuid
import time
from sentence_transformers import SentenceTransformer
from src.embedding_model import get_embedding
import warnings


# Suppress DeprecationWarning specifically for `search` method
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*search.*")


# Initialize Qdrant client
qdrant_client = QdrantClient(host="localhost", port=6333)

# Qdrant Collection Name and Vector Dimension
COLLECTION_NAME = "pdf_embeddings"
#VECTOR_DIM = 3072  # Should match the embedding dimensions


# Function to search embeddings in Qdrant
def search_embeddings(query, model_choice, top_k=3):
    query_embedding = get_embedding(query, model_choice)

    # Perform the search in Qdrant
    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=top_k,
        with_payload=True  # Include metadata in the search result
    )

    # Process the results
    top_results = [
        {
            "file": result.payload.get("file", "Unknown file"),
            "page": result.payload.get("page", "Unknown page"),
            "chunk": result.payload.get("chunk", "Unknown chunk"),
            "similarity": result.score,
        }
        for result in search_result
    ]

    # Print results for debugging
    #for result in top_results:
        #print(f"---> File: {result['file']}, Page: {result['page']}, Chunk: {result['chunk']}, Similarity: {result['similarity']:.2f}")

    return top_results

# Function to generate RAG (Retrieve and Generate) response
def generate_rag_response(query, context_results, llm_choice):
    # Prepare context string
    context_str = "\n".join(
        [
            f"From {result['file']} (page {result['page']}, chunk {result['chunk']}) "
            f"with similarity {result['similarity']:.2f}"
            for result in context_results
        ]
    )

    # Construct the prompt with the context
    prompt = f"""You are a helpful AI assistant. 
    Use the following context to answer the query as accurately as possible. If the context is 
    not relevant to the query, say 'I don't know'.

Context:
{context_str}

Query: {query}

Answer:"""

    if llm_choice == 1:
        # Generate response using Ollama
        response = ollama.chat(
            model="llama3.2:latest", messages=[{"role": "user", "content": prompt}]
        )

        
    elif llm_choice == 2:
        # Generate response using Mistral
        response = ollama.chat(
            model="mistral", messages=[{"role": "user", "content": prompt}]
        )

    
    return response["message"]["content"]

# Interactive search interface
def interactive_search(model_choice, llm_choice):
    """Interactive search interface."""
    print("🔍 RAG Search Interface")
    print("Type 'exit' to quit")

    while True:
        query = input("\nEnter your search query: ")

        if query.lower() == "exit":
            break
        
        start_time = time.time()
        # Search for relevant embeddings in Qdrant
        context_results = search_embeddings(query, model_choice)
        end_time = time.time()
        total_time = end_time - start_time
        
        # Generate RAG response
        s2 = time.time()
        response = generate_rag_response(query, context_results, llm_choice)
        e2 = time.time()
        tot2 = e2 - s2

        print(f" Total Search Time: {total_time:.2f} seconds")
        print(f" Total RAG Response Time: {tot2:.2f} seconds")


        print("\n--- Response ---")
        print(response)


# Main entry
if __name__ == "__main__":
    # user input of embedding model
    model_choice = int(input("\n* 1 for SentenceTransformer MiniLM-L6-v2\n* 2 for SentenceTransformer mpnet-base-v2\n* 3 for mxbai-embed-large"
    "\nEnter the embedding model choice (make sure its consistent with ingest.py): "))

    # user input of llm model
    llm_choice = int(input("\n* 1 for Ollama\n* 2 for Mistral"
    "\nEnter the LLM model choice: "))


    interactive_search(model_choice, llm_choice)  # Start the interactive search interface
