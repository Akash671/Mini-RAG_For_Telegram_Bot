"""
author : @akash
rag.py


purpose:
1. Handle the Retrieval-Augmented Generation (RAG) logic:
   - Caching query embeddings to speed up repeated queries.
    - Retrieving relevant document chunks based on query embeddings.
    - Managing conversation history to provide context to the LLM while avoiding "Memory Bleed".
    - Strict system instructions to ensure the LLM only answers based on retrieved context and doesn't hallucinate.
"""

import numpy as np
from config import HF_API_TOKEN, MODEL_ID, user_history
from huggingface_hub import InferenceClient
from embed import create_embeddings
from db import search, get_cached_embedding, save_to_cache

# Configuration
HF_API_TOKEN = HF_API_TOKEN
MODEL_ID = MODEL_ID

client = InferenceClient(api_key=HF_API_TOKEN)
user_history = {} 

def get_llm_response(user_id, query):
    # --- 1. Caching ---
    cached_vector_blob = get_cached_embedding(query)
    if cached_vector_blob:
        query_vector = np.frombuffer(cached_vector_blob, dtype=np.float32)
    else:
        query_vector = create_embeddings([query])[0]
        save_to_cache(query, query_vector)

    # --- 2. Retrieval ---
    context_results = search(query_vector, k=3)
    context_strings = []
    unique_sources = set()
    
    for res in context_results:
        context_strings.append(f"Source [{res['source']}]: {res['text']}")
        unique_sources.add(res['source'])
    
    context_text = "\n".join(context_strings)

    # --- 3. History Management ---
    if user_id not in user_history:
        user_history[user_id] = []
    
    # CRITICAL: Strict System Instruction
    system_instruction = (
        "You are a Telecom Assistant. Use the 'CURRENT SEARCH CONTEXT' to answer. "
        "If the answer is NOT in the context, say 'I don't know'. "
        "Ignore the 'CONVERSATION HISTORY' if it discusses a different topic than the CURRENT QUESTION."
    )

    messages = [{"role": "system", "content": system_instruction}]

    # Only include the last 2 interactions (4 messages) to reduce "Memory Bleed"
    if user_history[user_id]:
        messages.append({"role": "system", "content": "--- START CONVERSATION HISTORY ---"})
        messages.extend(user_history[user_id][-4:])
        messages.append({"role": "system", "content": "--- END CONVERSATION HISTORY ---"})

    # Clearer separation of tasks
    prompt_content = (
        f"CURRENT SEARCH CONTEXT:\n{context_text}\n\n"
        f"CURRENT QUESTION: {query}\n\n"
        f"Answer the current question using ONLY the context provided above:"
    )
    
    messages.append({"role": "user", "content": prompt_content})

    try:
        # 4. Generate response
        response = client.chat_completion(
            model=MODEL_ID,
            messages=messages,
            max_tokens=250,
            temperature=0.0  # Set to 0.0 for maximum factual consistency
        )
        
        raw_answer = response.choices[0].message.content

        # 5. Update History (Save the RAW answer, NOT the source footer)
        # This prevents the LLM from seeing technical source metadata in history
        user_history[user_id].append({"role": "user", "content": query})
        user_history[user_id].append({"role": "assistant", "content": raw_answer})

        # 6. Final Format for User
        sources_footer = "\n\n### **Sources:** " + ", ".join(unique_sources)
        return raw_answer + sources_footer

    except Exception as e:
        return f"Support Bot Error: {str(e)}"