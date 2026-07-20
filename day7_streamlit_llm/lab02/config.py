import os, sys
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
DB_NAME = os.getenv("DB_NAME", "review_history.db")

if not GEMINI_API_KEY:
    print("Configuration Error: GEMINI_API_KEY environment variable is missing!")
    sys.exit(1)

if not GEMINI_MODEL:
    print("Configuration Error: GEMINI_MODEL environment variable is missing!")
    sys.exit(1)

if not DB_NAME:
    print("Configuration Error: DB_NAME environment variable is missing!")
    sys.exit(1)