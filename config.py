"""
author : @akash
config.py

purpose:
1. Centralized configuration file to store all constants, API keys, model names, database settings, and global shared state.
2. This allows for easy management and modification of settings without having to search through multiple files.
3. By importing this config module in other parts of the application, we ensure that all components are using the same configuration values, reducing the risk of inconsistencies and making the codebase cleaner.
"""

import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# API Keys and Tokens - Pulled from .env
# The second argument is a fallback/default value if the .env key is missing
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Model Configurations
MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"
EMBED_MODEL_NAME = 'all-MiniLM-L6-v2'

# Database Settings
DB_NAME = "mini_rag.db"

# update this path to your actual DLL location
# C:\Users\YOUR_USER_NAME\AppData\Local\Programs\Python\Python39\lib\site-packages\sqlite_vec\vec0.dll"

VEC0_PATH = r"C:\Users\ATT\AppData\Local\Programs\Python\Python39\lib\site-packages\sqlite_vec\vec0.dll"

# Global Shared State
# Storing this here allows both app.py and rag2.py to access/modify the same object
user_history = {}