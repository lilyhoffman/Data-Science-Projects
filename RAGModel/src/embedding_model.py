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
    :return: The embedding as a list or None if an error occurs
    """
    # Validate model_choice input
    if model_choice not in [1, 2, 3]:
        print("Invalid model choice. Please select a model between 1 and 3.")
        return None

    try:
        if model_choice == 1:
            embedding = embedding_model_1.encode(text).tolist()
            return embedding

        elif model_choice == 2:
            embedding = embedding_model_2.encode(text).tolist()
            return embedding

        elif model_choice == 3:
            # Handling Ollama API call for model 3
            response = ollama.embeddings(model=embedding_model_3, prompt=text)
            if 'embedding' in response:
                return response["embedding"]
            else:
                print("Error: Ollama API response does not contain 'embedding'.")
                return None

    except Exception as e:
        print(f"Error occurred while getting embedding: {e}")
        return None

