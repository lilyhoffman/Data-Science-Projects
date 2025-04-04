import chromadb
import json
from sentence_transformers import SentenceTransformer
import time
from memory_profiler import memory_usage
from src.embedding_model import get_embedding


# create an embedding based on user input
def encode_text(info, model_choice):

    return get_embedding(info, model_choice)

# create the Chroma client; need PersistentClient and not Client because we do not want
# data disappearing
def create_chroma_client(path="./chroma_db"):
    client = chromadb.PersistentClient(path=path)
    try:
        client.delete_collection(name="ds4300_course_notes")
    except:
        pass

    return client.get_or_create_collection(name="ds4300_course_notes")

"""chroma_client = chromadb.PersistentClient(path="./chroma_db")

#Create collection to index; pulling from existing preprocesed data
stored_collection = chroma_client.get_or_create_collection(name="ds4300_course_notes")"""

# compute time and memory usage of db
def log_chroma_performance(start_time, memory_usage, end_time):
    total_time = end_time - start_time
    highest_memory_usage = max(memory_usage)

    print(f" Total Execution Time: {total_time:.2f} seconds")
    print(f"Peak Memory Usage: {highest_memory_usage:.2f} MB")


# obtain embeddings, create ids for them, and proceed to store them
def store_embedding(info, chunk_size, model_choice):
    information = encode_text(info, model_choice)
    stored_collection = create_chroma_client()

    # create an id and then add it to the stored collection, also handle duplicates
    id_gen = str(hash(info))
    current_docs = stored_collection.get(ids=[id_gen])
    # now apply check
    if current_docs and len(current_docs["documents"]) > 0:
        print("Skipping already-made ids")
        return 

    # store in the db
    stored_collection.add(documents=[info], embeddings=[information], ids=[id_gen], metadatas=[{"chunk_size": chunk_size}])
    print(f'Values have been stored: {info[:50]}')
    print(f'Stored values: (size {chunk_size}): {info[:50]}')

# process documents based on chunking size and overlap
def process_docs(data, model_choice, target_chunk_size, target_overlap):
    for i in data["processed_pdfs"]:
        title = i.get("title", "Unknown Title")
        print(f'Title processing: {title}')
        for key, chunked_material in i.get("chunked_content", {}).items():
            
            # obtain key of chunked text
            try:
                parts = key.split("_")
                chunk_size = int(parts[0])
                overlap = int(parts[-1])
                # Filter based on inputs
                if (target_chunk_size == chunk_size and target_overlap == overlap):
                    for j in chunked_material:
                        store_embedding(j, chunk_size, model_choice)

            except Exception as e:
                continue
            

            
# pull from json database
def pull_from_json(path, model_choice):

    try: 

        # open and process the data
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)


        # determine chunk size and overlap
        chunk_size = int(input("\n* Chunk size: "))
        overlap = int(input("* Overlap: "))

        start_time = time.time()
        memory_data = memory_usage((process_docs, (data, model_choice, chunk_size, overlap), {}), interval=0.1)
        end_time = time.time()
        log_chroma_performance(start_time, memory_data, end_time)

        print("Embeddings were stored.")

        #Add in exception when fails:
    except Exception as e:
        print(f'There was an error with the json file: {e}')



#Get path to json data
def main():
    model_choice = int(input("\n* 1 for SentenceTransformer MiniLM-L6-v2\n* 2 for SentenceTransformer mpnet-base-v2\n* 3 for mxbai-embed-large"
    "\nEnter the embedding model choice:"))
    
    if model_choice == 1:
        print("Using SentenceTransformer for embeddings.")

    elif model_choice == 2:
        print("Using SentenceTransformer for embeddings.")

    elif model_choice == 3:
        print("Using Ollama for embeddings.")


    path = "data/processed_json/ds4300_course_notes.json"
    pull_from_json(path, model_choice)

if __name__ == "__main__":
    main()