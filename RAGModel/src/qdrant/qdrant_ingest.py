import os
import numpy as np
import fitz
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from qdrant_client.http.models import ScoredPoint
import ollama
import uuid
import time
from memory_profiler import memory_usage
from src.embedding_model import get_embedding


# Qdrant Client Setup
qdrant_client = QdrantClient("localhost", port=6333)  # Adjust as per your setup

# Qdrant Collection Name and Vector Dimension
COLLECTION_NAME = "pdf_embeddings"

# Create the Qdrant collection
def create_qdrant_collection(VECTOR_DIM):
    try:
        qdrant_client.delete_collection(collection_name=COLLECTION_NAME)
    except Exception as e:
        print(f"Error deleting existing collection: {e}")
    
    # Create the collection with the appropriate vector params
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
        size=VECTOR_DIM,  # Vector dimension (must match your embedding model output)
        distance=Distance.COSINE  # Similarity metric
    )
    )
    print("Qdrant collection created successfully.")


# measure metrics including time and memory usage
def log_qdrant_performance(start_time, memory_usage, end_time):
    total_time = end_time - start_time
    highest_memory_usage = max(memory_usage)

    print(f" Total Execution Time: {total_time:.2f} seconds")
    print(f"Peak Memory Usage: {highest_memory_usage:.2f} MB")



points = []
# Store the embedding in Qdrant
def store_embedding(file: str, page: str, chunk: str, embedding: list):

    # Creating a unique point ID for the document (file, page, and chunk)
    point_id = str(uuid.uuid4()) 
    
    # Convert embedding to a list of floats
    embedding_vector = np.array(embedding, dtype=np.float32).tolist()
    

    points.append(PointStruct(id=point_id, vector=embedding_vector, payload={"file": file, "page": page, "chunk": chunk}))


    # Prepare and insert the point into Qdrant
    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    

# Extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc = fitz.open(pdf_path)
    text_by_page = []
    for page_num, page in enumerate(doc):
        text_by_page.append((page_num, page.get_text()))
    return text_by_page

# Split text into chunks with overlap
def split_text_into_chunks(text, chunk_size, overlap):
    """Split text into chunks of approximately chunk_size words with overlap."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
    return chunks

# Process all PDF files in a given directory
def process_pdfs(data_dir, model_choice, chunk_size, overlap):
    count = 0
    for file_name in os.listdir(data_dir):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(data_dir, file_name)
            text_by_page = extract_text_from_pdf(pdf_path)
            for page_num, text in text_by_page:
                chunks = split_text_into_chunks(text, chunk_size, overlap)
                for chunk_index, chunk in enumerate(chunks):
                    embedding = get_embedding(chunk, model_choice)
                    store_embedding(
                        file=file_name,
                        page=str(page_num),
                        chunk=str(chunk),
                        embedding=embedding,
                    )
            count += 1
            print(f" -----> Processed {file_name}")
    print(f"Total processed files: {count}")


def main():
    # user input of embedding model choice
    model_choice = int(input("\n* 1 for SentenceTransformer MiniLM-L6-v2\n* 2 for SentenceTransformer mpnet-base-v2\n* 3 for mxbai-embed-large"
    "\nEnter the embedding model choice:"))
    
    if model_choice == 1:
        print("Using SentenceTransformer for embeddings.")
        VECTOR_DIM = 384
    elif model_choice == 2:
        print("Using SentenceTransformer for embeddings.")
        VECTOR_DIM = 768
    elif model_choice == 3:
        print("Using Ollama for embeddings.")
        VECTOR_DIM = 1024

    # define chunk size and overlap
    chunk_size = int(input("\n* Chunk size: "))
    overlap = int(input("* Overlap: "))

    # create qdrant db
    create_qdrant_collection(VECTOR_DIM)

    # ingest files into qdrant db
    start_time = time.time()
    memory_data = memory_usage((process_pdfs, ('data/unprocessed_pdfs', model_choice, chunk_size, overlap), {}), interval=0.1)
    end_time = time.time()
    log_qdrant_performance(start_time, memory_data, end_time)


    print("\n---Done processing PDFs---\n")


if __name__ == "__main__":
    main()
