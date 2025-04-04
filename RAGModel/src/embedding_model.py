from sentence_transformers import SentenceTransformer
import ollama

# Initialize the SentenceTransformer model
embedding_model_1 = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embedding_model_2 = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
embedding_model_3 = 'mxbai-embed-large'


def get_embedding(text: str, model_choice: int):
    """
    Get the embedding based on the selected model.
    :param text: The text to embed
    :param model_choice: The model choice (1, 2, or 3)
    :return: The embedding as a list
    """
    if model_choice == 1:
        # Using SentenceTransformer
        #print("Using SentenceTransformer for embeddings.")
        embedding = embedding_model_1.encode(text).tolist()
        return embedding
    
    elif model_choice == 2:
        # Using SentenceTransformer
        #print("Using SentenceTransformer for embeddings.")
        embedding = embedding_model_2.encode(text).tolist()
        return embedding
    
    elif model_choice == 3:
        # Optionally, implement a third embedding model here
        #print("Using Ollama for embeddings.")
        response = ollama.embeddings(model=embedding_model_3, prompt=text)
        return response["embedding"]

        #response = ollama.embeddings(model="llama3.2", prompt=text)
        #return response["embedding"]
    else:
        print("Invalid model choice.")
        return None
