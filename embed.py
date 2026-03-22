"""
author : @akash
embed.py


purpose:
1. Load documents, preprocess, chunk, and create embeddings using SentenceTransformer.
"""

import os
import numpy as np
from sentence_transformers import SentenceTransformer
# Import from your db script (using 'db' as per your provided code)
from db import init_db, store_embedding, search, get_cached_embedding, save_to_cache
from config import EMBED_MODEL_NAME

# ==========================================================
# OPTIMIZATION: Load the model ONCE globally
# This stays in RAM and is reused for every function call.
# ==========================================
print("### Loading SentenceTransformer model...")
EMBED_MODEL = SentenceTransformer(EMBED_MODEL_NAME)
print("### Model loaded and ready.")

def load_docs_with_sources(folder_path):
    """
    Returns a list of tuples: [(file_content, filename), ...]
    """
    documents = []
    if not os.path.exists(folder_path):
        print(f"Error: Folder {folder_path} not found.")
        return documents

    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                documents.append((content, filename))
    return documents

def docs_pre_processing(docs):
    """Simple cleaning: remove extra newlines."""
    return docs.replace('\n', ' ').strip()

def chunk_doc(doc, filename, chunk_size=400, overlap=50):
    """
    Splits text into chunks and tracks their source filename.
    """
    chunks = []
    sources = []
    start = 0
    while start < len(doc):
        end = start + chunk_size
        chunk = doc[start:end]
        chunks.append(chunk)
        sources.append(filename)
        start += chunk_size - overlap
    return chunks, sources

def create_embeddings(chunks):
    """
    Uses the GLOBAL model to encode text chunks.
    No longer re-loads the model on every call.
    """
    embeddings = EMBED_MODEL.encode(
        chunks,
        show_progress_bar=False  # Disabled for cleaner bot logs
    )
    return embeddings

if __name__ == "__main__":
    # Path to your data folder
    raw_data_folder_path = r'C:\Akash\AA\AI\Mini-RAG_For_Telegram_Bot\data'
    
    # 1. Initialize Database
    init_db()

    # 2. Load and Chunk
    raw_docs = load_docs_with_sources(raw_data_folder_path)
    
    all_chunks = []
    all_sources = []

    print("### Processing documents...")
    for content, filename in raw_docs:
        cleaned_content = docs_pre_processing(content)
        chunks, sources = chunk_doc(cleaned_content, filename)
        all_chunks.extend(chunks)
        all_sources.extend(sources)

    # 3. Create and Store Embeddings (if DB is empty or needs refresh)
    if all_chunks:
        print(f"Creating embeddings for {len(all_chunks)} chunks...")
        embeddings = create_embeddings(all_chunks)
        store_embedding(all_chunks, embeddings, all_sources)
        print(f"### Successfully stored chunks in the database.")

    # 4. Test Search with Caching Optimization
    user_query = "How do I activate my new SIM card?"
    print(f"\n--- Testing Query Optimization ---")
    print(f"User Question: {user_query}")

    # Check Cache first (Optimization)
    cached_vector_blob = get_cached_embedding(user_query)
    
    if cached_vector_blob:
        print("### [Cache Hit] Using stored vector. No model inference needed!")
        query_vector = np.frombuffer(cached_vector_blob, dtype=np.float32)
    else:
        print("### [Cache Miss] Generating new vector using global model...")
        query_vector = create_embeddings([user_query])[0]
        save_to_cache(user_query, query_vector)

    # Perform Vector Search
    top_results = search(query_vector, k=3)
    
    print("\n--- Results ---")
    for idx, res in enumerate(top_results):
        print(f"{idx + 1}. [Source: {res['source']}]")
        print(f"   Snippet: {res['text'][:100]}...\n")