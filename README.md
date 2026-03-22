## Telecom RAG Telegram Bot
An AI-powered Telegram Assistant built with a Retrieval-Augmented Generation (RAG) architecture. The bot answers telecom-related queries based on local documents, maintains a short-term conversation history, and uses SQLite for high-performance vector caching.

## Features
Document Retrieval: Searches through local .txt files to find the most relevant context.

Conversation Memory: Remembers the last 2-3 interactions per user for follow-up questions.

Query Caching: Saves vector embeddings in SQLite to reduce API latency and costs.

Portable Design: Uses relative paths and .env configuration for easy deployment on any machine.

Source Transparency: Every answer includes a list of the source files used to generate it.

## Project Structure
Plaintext
Mini-RAG_For_Telegram_Bot/
├── data/               # Drop your .txt documents here
├── app.py              # Telegram Bot Interface & Handlers
├── rag2.py             # RAG Logic, Prompt Engineering & History
├── embed.py            # Sentence-Transformers Embedding Logic
├── db.py               # SQLite & Vector Extension Management
├── config.py           # Centralized Settings & Path Handling
├── .env                # Private API Keys (DO NOT SHARE)
└── requirements.txt    # Project Dependencies

## Setup Instructions
1. Clone the Repository
Bash
git clone <your-repo-url>
cd Mini-RAG_For_Telegram_Bot
2. Install Dependencies
It is recommended to use a virtual environment:

Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
3. Configure Environment Variables
Create a .env file in the root directory:

Code snippet
HF_API_TOKEN=your_huggingface_token_here
TELEGRAM_TOKEN=your_telegram_bot_token_here
4. Prepare your Data
Place all your reference text files (e.g., policies.txt, faqs.txt) inside the /data folder.

## Usage
Step 1: Embed the Documents
Run the embedding script to process your text files into the SQLite database:

Bash
python embed.py
Step 2: Start the Bot
Launch the Telegram bot:

Bash
python app.py
Step 3: Chat
Open Telegram and find your bot.

/start: Initialize the bot.

/ask <question>: Ask a specific question.

/clear: Wipe your conversation history and start fresh.

Or just type your question directly!

## How it Works (System Design)
Input: The user sends a question to the Telegram Bot.

Caching: The system checks if that exact question has been asked before in the query_cache table.

Retrieval: If not cached, the query is converted to a vector and matched against the vec_table using cosine similarity.

Context Construction: The top 3 relevant text chunks are pulled and combined with the user's recent Message History.

Generation: A prompt is sent to the Llama-3.2-1B-Instruct model on Hugging Face.

Response: The bot replies with an answer and cites the source files.

## License
Distributed under the MIT License. See LICENSE for more information.

Author: @akash



## Demo 

![alt text](demo.png)
