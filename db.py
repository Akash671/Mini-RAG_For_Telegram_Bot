"""
auhtor : @akash
db.py

purpose:
1. Initialize the SQLite database with VEC0 extension for vector storage.
2. Store document chunks, their embeddings, and source information.
3. Implement a caching mechanism to store and retrieve query embeddings, reducing redundant computations for repeated queries.
4. Provide a search function to retrieve relevant document chunks based on query embeddings.
5. Ensure that the database schema supports efficient retrieval and caching while maintaining simplicity.
"""


import sqlite3
import numpy as np
import os
from config import DB_NAME, VEC0_PATH


# Update this path to your actual DLL location
VEC0_PATH = VEC0_PATH
def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.enable_load_extension(True)
    conn.load_extension(VEC0_PATH)
    c = conn.cursor()
    
    # 1. UPDATED: vec_table now includes a 'source' column for Source Snippets
    c.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_table
        USING vec0(
            embedding FLOAT[384],
            text TEXT,
            source TEXT
        )
    """)
    
    # 2. NEW: Cache table to store already generated embeddings
    c.execute("""
        CREATE TABLE IF NOT EXISTS query_cache (
            query_text TEXT PRIMARY KEY,
            embedding_blob BLOB
        )
    """)
    
    conn.commit()
    conn.close()

# --- CACHING FUNCTIONS ---

def get_cached_embedding(query):
    """Retrieve embedding from cache if it exists."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT embedding_blob FROM query_cache WHERE query_text = ?", (query,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def save_to_cache(query, vector):
    """Save a new embedding to the cache."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    vector_blob = np.array(vector, dtype=np.float32).tobytes()
    c.execute("INSERT OR IGNORE INTO query_cache (query_text, embedding_blob) VALUES (?, ?)", 
              (query, vector_blob))
    conn.commit()
    conn.close()

# --- STORAGE & SEARCH ---

def store_embedding(chunks, vectors, sources):
    """
    chunks: list of text
    vectors: list of embeddings
    sources: list of filenames corresponding to each chunk
    """
    conn = sqlite3.connect(DB_NAME)
    conn.enable_load_extension(True)
    conn.load_extension(VEC0_PATH)
    c = conn.cursor()

    for chunk, vector, source in zip(chunks, vectors, sources):
        vector_blob = np.array(vector, dtype=np.float32).tobytes()
        
        # Now inserting the source (filename) along with text
        c.execute(
            "INSERT INTO vec_table (embedding, text, source) VALUES (?, ?, ?)",
            (vector_blob, chunk, source)
        )

    conn.commit()
    conn.close()

def search(query_vector, k=3):
    conn = sqlite3.connect(DB_NAME)
    conn.enable_load_extension(True)
    conn.load_extension(VEC0_PATH)
    c = conn.cursor()

    query_blob = np.array(query_vector, dtype=np.float32).tobytes()

    # UPDATED: We now select 'text' AND 'source'
    c.execute("""
        SELECT text, source, distance
        FROM vec_table
        WHERE embedding MATCH ?
          AND k = ?
        ORDER BY distance
    """, (query_blob, k))
    
    # Return list of dictionaries for easier handling in rag.py
    results = [{"text": row[0], "source": row[1]} for row in c.fetchall()]
    conn.close()
    return results

if __name__ == "__main__":
    init_db()