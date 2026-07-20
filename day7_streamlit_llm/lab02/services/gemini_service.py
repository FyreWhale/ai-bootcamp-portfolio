from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL

def init_gemini():
    return genai.Client(api_key=GEMINI_API_KEY)

def call_gemini_model(review_content, system_prompt, temperature=0.1):
    client = init_gemini()
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=review_content,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature
            )
        )
        return response.text
    except Exception as api_err:
        raise Exception(f"❌ Gemini API Error: {api_err}")
    
def parse_gemini_response(raw_output):
    clean_summary = raw_output
    rating = 5
    if "FINAL_RATING:" in raw_output:
            parts = raw_output.split("FINAL_RATING:")
            clean_summary = parts[0].strip()
            try:
                # Clean extract trailing numerical characters
                rating = int("".join(filter(str.isdigit, parts[1])))
            except ValueError:
                rating = 5
    
    return clean_summary, rating

def analyze_review_sentiment(review_content):
    # Define structural prompt system rules
    system_prompt = (
        "You are a database-integrated text processing utility. Analyze the user text data. "
        "You MUST output your response in a strict formatted style containing two sections:\n"
        "1. A bulleted summary synthesized from the reviews.\n"
        "2. A standalone single line stating exactly: 'FINAL_RATING: X' (where X is an integer score from 0 to 10).\n\n"
        "Keep your response analytical and professional."
    )
    
    raw_output = call_gemini_model(review_content, system_prompt)
    clean_summary, rating = parse_gemini_response(raw_output)
    
    # Determine Category routing bracket
    if 8 <= rating <= 10:
        category = "Good"
    elif 4 <= rating <= 7:
        category = "Average"
    else:
        category = "Bad"

    return clean_summary, rating, category
