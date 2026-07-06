from mem0 import Memory

MODEL = "gemma4:e2b"
OLLAMA = "http://localhost:11434"

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
            "ollama_base_url": OLLAMA
        }
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": MODEL,
            "ollama_base_url": OLLAMA
        }
    }
}

m = Memory.from_config(config_dict=config)

# Adding a fact for a specific user
print("Attempting to store fact...")
m.add("My name is John Doe", user_id="student1")
print("Fact stored successfully.")

results = m.search(query="What is my name?", filters={"user_id": "student1"})
print("\nSearch Results:")
print(results)