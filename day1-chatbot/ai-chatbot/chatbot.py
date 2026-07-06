import os
from mem0 import Memory
from litellm import completion

USER_ID = "fyrewhale"
MODEL = "gemma4:e2b"
MODEL_PATH = "ollama/gemma4:e2b"
OLLAMA_BASE_URL = "http://localhost:11434"

config = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "local_memory",
            "path": "./chroma_db",
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": OLLAMA_BASE_URL
        }
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": MODEL,
            "ollama_base_url": OLLAMA_BASE_URL
        }
    }
}

m = Memory.from_config(config_dict=config)

def chat(input, history):
    search_results = m.search(query=input, filters={"user_id": USER_ID})

    memory_context = ""
    if search_results and 'results' in search_results:
        facts = [res['memory'] for res in search_results['results']]
        if facts:
            memory_context = "- " + "\n- ".join(facts)

    system_prompt = (
        "You are a helpful conversational assistant. Use the following facts "
        "to personalize your responses if they are relevant to the conversation.\n\n"
        f"Relevant Facts:\n{memory_context if memory_context else 'None'}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    
    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": input})

    response = completion(
        model=MODEL_PATH,
        messages=messages,
        api_base=OLLAMA_BASE_URL
    )

    assistant_reply = response.choices[0].message.content

    conversation_turn = [
        {"role": "user", "content":  input},
        {"role": "assistant", "content": assistant_reply}
    ]
    m.add(messages=conversation_turn, user_id=USER_ID)

    return assistant_reply

# --- Interface ---
if __name__ == "__main__":
    print("Chatbot ready! Type 'quit' to exit.")
    
    # Initialize an empty list to store conversation history
    conversation_history = []
    
    while True:
        try:
            user_input = input("\nYou: ")
            
            if user_input.strip().lower() in ['quit', 'exit']:
                print("Exiting chatbot. Goodbye!")
                break
                
            if not user_input.strip():
                continue
                
            # Pass the current input AND the history so far
            reply = chat(user_input, conversation_history)
            print(f"Bot: {reply}")
            
            # Update the history for the NEXT turn
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": reply})
            
        except KeyboardInterrupt:
            print("\nExiting chatbot. Goodbye!")
            break