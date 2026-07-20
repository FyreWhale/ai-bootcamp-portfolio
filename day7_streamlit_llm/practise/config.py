import os
import sys
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Read the environment variables with safe defaults
MODEL_NAME = os.getenv("MODEL_NAME")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

# Read the Gemini API key and model from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")

if not GEMINI_API_KEY:
    print("Security Error: GEMINI_API_KEY is missing from your .env file!")
    print("Please generate a key at https://aistudio.google.com/ and add it to .env")
    sys.exit(1)

# Database configuration
DB_NAME = os.getenv("DB_NAME", "chat_history.db")

# Default model to use if not specified in the UI
DEFAULT_MODEL = MODEL_NAME if MODEL_NAME else "llama3:latest"