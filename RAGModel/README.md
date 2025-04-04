# RAG-volution: Retrieval-Augmented Generation System  

## Overview  
RAG-volution is a Retrieval-Augmented Generation (RAG) system that allows users to query a collection of DS4300 course notes and receive accurate, context-driven responses. Our system leverages document ingestion, embedding indexing, and locally-run large language models (LLMs) to optimize retrieval and synthesis of information.  

## Features  
- **Efficient Document Retrieval**: Uses vector databases to store and retrieve relevant course materials.  
- **Multiple Embedding Models**: Experimentation with different embedding models for optimal performance.  
- **Chunking Strategies**: Comparison of various chunk sizes and overlaps to balance retrieval quality and efficiency.  
- **Locally-Run LLMs**: Evaluation of models such as Ollama3:2 and Mistral for response generation.  
- **Scalability**: Designed for flexibility and adaptation to different dataset sizes and user needs.  

## Technology Stack  
- **Programming Language**: Python  
- **Vector Databases**: Redis, ChromaDB, Qdrant  
- **Embedding Models**:  
  - `sentence-transformers/all-MiniLM-L6-v2`  
  - `sentence-transformers/all-mpnet-base-v2`  
  - `mxbai-embed-large`  
- **LLMs**:  
  - Ollama3:2  
  - Mistral  

## Data Processing  
- Conversion of course PDFs into structured JSON format.  
- Testing of different chunk sizes (200, 500, 1000 tokens) and overlaps (0, 50, 100 tokens).  
- Analysis of indexing speed vs. retrieval accuracy.  

## Experimental Design  
- Evaluated combinations of chunk size, overlap, embedding models, and vector databases.  
- Measured retrieval quality, speed, and memory usage.  
- Tested queries including:  
  - **"What are the ACID components?"**  
  - **"Write a MongoDB query to return thriller movies from 2005-2012."**  
  - **"What is the difference between a B+ tree and an AVL tree?"**  

  ## Setup Instructions  

### Install Docker  
To run the Redis server and other dependencies, you must install Docker:  

- [Download Docker](https://www.docker.com/get-started) and install it based on your operating system.  

### Run Redis in Docker  
1. Pull the Redis Docker image
2. Start a Redis container and expose it on port 6379

### Run Qdrant in Docker
1. Pull the Qdrant Docker image
2. Start a Qdrant container and expose it on port 6333

## How to Run
1. Clone the repository:  
  ```bash
  git clone https://github.com/Mihalis-Koutouvos/DS4300_Practical_2_LLM_Analysis.git
  ```

2. Install required packages and libaries
  ```bash
  pip install -r src/requirements.txt
  ```

3. Run ingest file to create database:
  ```bash
  python3 -m src.{db_folder_name}.{db_name}_ingest
  ```

4. Run search file to generate RAG response:
  ```bash
  python3 -m src.{db_folder_name}.{db_name}_search
  ```

5. To run the last embedding model ('mxbai-embed-large'), make sure to pull model with Ollama.
```bash
ollama pull mxbai-embed-large
```

