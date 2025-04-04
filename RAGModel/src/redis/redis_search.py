import redis
import json
import numpy as np
import time
#from sentence_transformers import SentenceTransformer
import ollama
from redis.commands.search.query import Query
from redis.commands.search.field import VectorField, TextField
from src.embedding_model import get_embedding


# Initialize models
redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

INDEX_NAME = "embedding_index"
DOC_PREFIX = "doc:"
DISTANCE_METRIC = "COSINE"

# generate embedding based on user input
def find_embedding(text, model):
    response = get_embedding(text, model)
    return response


def search_embeddings(query, model_choice, top_k=3):
    start_time = time.time() 
    query_embedding = find_embedding(query, model_choice)
    # Convert embedding to bytes for Redis search
    query_vector = np.array(query_embedding, dtype=np.float32).tobytes()

    try:
        # Construct the vector similarity search query
        # Use a more standard RediSearch vector search syntax
        # q = Query("*").sort_by("embedding", query_vector)

        q = (
            Query("*=>[KNN 5 @embedding $vec AS vector_distance]")
            .sort_by("vector_distance")
            .return_fields("id", "file", "page", "chunk", "vector_distance")
            .dialect(2)
        )

        # Perform the search
        results = redis_client.ft(INDEX_NAME).search(
            q, query_params={"vec": query_vector}
        )

        # Transform results into the expected format
        top_results = [
            {
                "file": result.file,
                "page": result.page,
                "chunk": result.chunk,
                "similarity": result.vector_distance,
            }
            for result in results.docs
        ][:top_k]

        # Print results for debugging
        for result in top_results:
            print(
                f"---> File: {result['file']}, Page: {result['page']}, Chunk: {result['chunk']}"
            )
        
        end_time = time.time()  # End timing
        print(f"🔹 Embedding search time: {end_time - start_time:.4f} seconds")

        return top_results

    except Exception as e:
        print(f"Search error: {e}")
        return []


def generate_rag_response(query, context_results, llm_choice):
    start_time = time.time() 
    # Prepare context string
    context_str = "\n".join(
        [
            f"From {result.get('file', 'Unknown file')} (page {result.get('page', 'Unknown page')}, chunk {result.get('chunk', 'Unknown chunk')}) "
            f"with similarity {float(result.get('similarity', 0)):.2f}"
            for result in context_results
        ]
    )

    print(f"context_str: {context_str}")

    # Construct prompt with context
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

    end_time = time.time()  # End timing
    print(f"🔹 Response generation time: {end_time - start_time:.4f} seconds")

    return response["message"]["content"]


def interactive_search(model_choice, llm_choice):
    """Interactive search interface."""
    print("🔍 RAG Search Interface")
    print("Type 'exit' to quit")

    while True:
        query = input("\nEnter your search query: ")

        if query.lower() == "exit":
            break

        # Search for relevant embeddings
        context_results = search_embeddings(query, model_choice)

        # Generate RAG response
        response = generate_rag_response(query, context_results, llm_choice)

        print("\n--- Response ---")
        print(response)


def main():
    # user input of embedding model
    model_choice = int(input("\n* 1 for SentenceTransformer MiniLM-L6-v2\n* 2 for SentenceTransformer mpnet-base-v2\n* 3 for mxbai-embed-large"
    "\nEnter the embedding model choice (make sure its consistent with ingest.py): "))
    
    # user input of llm model
    llm_choice = int(input("\n* 1 for Ollama\n* 2 for Mistral"
    "\nEnter the LLM model choice: "))

    interactive_search(model_choice, llm_choice)


if __name__ == "__main__":
    main()
