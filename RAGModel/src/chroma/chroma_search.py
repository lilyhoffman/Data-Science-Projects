import chromadb
from sentence_transformers import SentenceTransformer
import ollama
import time
from src.embedding_model import get_embedding

#Create the Chroma client; need PersistentClient and not Client because we do not want
#data disappearing
chroma_client = chromadb.PersistentClient(path="./chroma_db")

#Create collection to index; pulling from existing preprocesed data
stored_collection = chroma_client.get_or_create_collection(name="ds4300_course_notes")


# create an embedding for a query
def encode_text(info, model_choice):
    response = get_embedding(info, model_choice)

    return response


# begin searching the embeddings
def search_embeddings(query, model_choice, top_k=3, chunk_size=None, overlap=None):
    start_time = time.time() 

    # encode
    encode_query = encode_text(query, model_choice)

    # build metadata filter if specified
    filter_conditions = {}
    if chunk_size is not None:
        filter_conditions["chunk_size"] = chunk_size
    if overlap is not None:
        filter_conditions["overlap"] = overlap
    
    # store results
    query_results = stored_collection.query(query_embeddings=[encode_query], n_results=top_k, where=filter_conditions if filter_conditions else None)

    # answer to if there are no answers to the query
    if not query_results or "documents" not in query_results or not query_results["documents"]:
        return []

    # get documents and necessary metadata (similar process as redis)
    obtained_documents = query_results["documents"][0]
    obtained_meta = query_results.get("metadatas", [[]])


    if isinstance(obtained_meta, list) and len(obtained_meta) > 0 and isinstance(obtained_meta[0], list):
        obtained_meta = obtained_meta[0]


    if not isinstance(obtained_meta, list) and len(obtained_meta) > 0 and isinstance(obtained_meta[0], list):
        obtained_meta = [{} for _ in obtained_documents]

   

    for i, pdf in enumerate(obtained_documents):
        
        chunk_size = obtained_meta[i].get("chunk_size", "Unknown Size") if i < len(obtained_meta) and isinstance(obtained_meta[i], dict) else "Unknown Size"


    end_time = time.time()  # End timing
    print(f"Embedding search time: {end_time - start_time:.4f} seconds")

    return obtained_documents







def generate_rag_response(query, context_results, llm_choice):
    start_time = time.time() 
    # prepare context string
    context_str = "\n".join(
        [
            f"Chunk {i+1}: {query_result}" for i, query_result, in enumerate(context_results)
        ]
    )


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

    end_time = time.time()
    print(f"🔹 Response generation time: {end_time - start_time:.4f} seconds")

    return response["message"]["content"]



# used to set up the conversation between user and AI
def interactive_search(model_choice, llm_choice, chunk_size, overlap):
    print("🔍 RAG Search Interface")
    print("Type 'exit' to quit")
    while True:
        query = input("\nEnter your search query: ")

        #exit case
        if query.lower() == 'exit':
            break

        # otherwise, generate the RAG response
        # Search for relevant embeddings

        context_results = search_embeddings(query, model_choice, chunk_size, overlap)

        # Generate RAG response
        rag_response = generate_rag_response(query, context_results, llm_choice)

        print("\n--- Response ---")
        print(rag_response)

def main():
    # user input of embedding model
    model_choice = int(input("\n* 1 for SentenceTransformer MiniLM-L6-v2\n* 2 for SentenceTransformer mpnet-base-v2\n* 3 for mxbai-embed-large"
    "\nEnter the embedding model choice (make sure its consistent with ingest.py): "))

    # user input of llm model
    llm_choice = int(input("\n* 1 for Ollama\n* 2 for Mistral"
    "\nEnter the LLM model choice: "))

    # determine chunk size and overlap
    chunk_size = int(input("\n* Chunk size: "))
    overlap = int(input("* Overlap: "))

    interactive_search(model_choice, llm_choice, chunk_size, overlap)

if __name__ == "__main__":
    main()
