from google import genai
from google.genai import types
import config

client = genai.Client(api_key=config.GEMINI_API_KEY)

def _convert_to_gemini_contents(messages):
    formatted_contents = []
    for msg in messages:
        if msg['role'] == 'system':
            continue
        gemini_role = "model" if msg['role'] == "assistant" else "user"
        formatted_contents.append(
            types.Content(role=gemini_role, parts=[types.Part.from_text(text=msg['content'])])
        )
    return formatted_contents

def get_ai_response_stream(messages):
    gemini_payload = _convert_to_gemini_contents(messages)
    api_config = types.GenerateContentConfig(system_instruction=config.SYSTEM_PROMPT)
    return client.models.generate_content_stream(
        model=config.GEMINI_MODEL,
        contents=gemini_payload,
        config=api_config
    )

def parse_stream_chunks(raw_stream):
    for chunk in raw_stream:
        if chunk.text:
            yield chunk.text