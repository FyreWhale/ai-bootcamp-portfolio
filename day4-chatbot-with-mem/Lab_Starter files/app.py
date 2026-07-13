"""
PROJECT 1 — Context-Aware Chatbot with Memory

Your task is to build a chatbot that can remember useful information from
previous messages and use that memory to answer later questions.

This chatbot should be able to:

1. Build a working chatbot interface
   - You may use Gradio or a simple CLI.
   - The chatbot should accept user input and return an AI response.

2. Maintain conversation history
   - Store both user messages and assistant replies.
   - Use recent conversation history so the chatbot can understand context.

3. Store memory
   - Use JSON, SQLite, or ChromaDB.
   - For the basic version, SQLite or JSON is enough.
   - Each message should be saved with at least:
       role      -> "user" or "assistant"
       content   -> the message text
       timestamp -> when the message was saved

4. Retrieve relevant memory
   - Do not send the entire history to the model every time.
   - Retrieve only useful memory.
   - Basic version: keyword search.
   - Advanced version: semantic search using embeddings / ChromaDB.

5. Use provided files from Moodle
   - Load skills.md as learner profile or background knowledge.
   - Load memory_seed.json as structured starting memory.
   - Add both into the system prompt when helpful.

6. Apply prompt engineering
   - Write a clear system prompt.
   - Tell the model how to use memory.
   - Tell the model not to invent personal facts.
   - Tell the model to say “I don’t know” if memory does not contain the answer.

7. Bonus features
   - Add summarization when the conversation becomes long.
   - Support multiple users with separate memory.
   - Improve latency by limiting how much memory is sent to the model.

Suggested structure:

- setup database / memory file
- load skills.md
- load memory_seed.json
- save_memory()
- search_memory()
- get_recent_history()
- build_messages()
- chat_bot()
- Gradio or CLI interface

Important idea:
main chatbot function should not do everything by itself.
It should coordinate smaller helper functions, similar to the AI pipeline idea:
input -> retrieve memory -> build prompt -> call model -> save response -> return output.
"""

import gradio
import json
import datetime
import os
import dotenv
import groq
import google.genai as genai

dotenv.load_dotenv()

MEMORY_FILE = os.getenv("MEMORY_FILE", "chat_memory.json")
MEMORY_SEED_FILE = os.getenv("MEMORY_SEED_FILE", "memory_seed.json")
SKILLS_FILE = os.getenv("SKILLS_FILE", "skills.md")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

groq_client = groq.Client(api_key=GROQ_API_KEY)
gemini_client = genai.Client(api_key=GOOGLE_API_KEY)

def load_memory():
      """Load memory from a JSON file."""
      if os.path.exists(MEMORY_FILE):
         with open(MEMORY_FILE, "r") as f:
            return json.load(f)
      return []

def init_memory():
     """Initialize memory by translating the complex memory_seed.json safely."""
     if not os.path.exists(MEMORY_FILE):
         seed_data = []
         
         if os.path.exists("memory_seed.json"):
             with open("memory_seed.json", "r") as f:
                 raw_seed = json.load(f)
             
             # Check if raw_seed is a dictionary
             if isinstance(raw_seed, dict):
                 # 1. Safe translation of past_interactions
                 interactions = raw_seed.get("past_interactions", [])
                 for item in interactions:
                     if isinstance(item, dict):
                         date_val = item.get("date", "Unknown Date")
                         topic_val = item.get("topic", "Unknown Topic")
                         summary_val = item.get("summary", "")
                         content_str = f"Prior Interaction on {date_val} - Topic: {topic_val}. Summary: {summary_val}"
                         seed_data.append({
                             "role": "assistant",
                             "content": content_str,
                             "timestamp": f"{date_val}T00:00:00" if date_val != "Unknown Date" else datetime.datetime.now().isoformat()
                         })
                     elif isinstance(item, str):
                         seed_data.append({
                             "role": "assistant",
                             "content": f"Prior Interaction: {item}",
                             "timestamp": datetime.datetime.now().isoformat()
                         })
                         
                 # 2. Safe translation of saved_facts
                 facts = raw_seed.get("saved_facts", [])
                 for fact in facts:
                     seed_data.append({
                         "role": "assistant",
                         "content": f"Saved Fact: {fact}",
                         "timestamp": datetime.datetime.now().isoformat()
                     })
                     
         with open(MEMORY_FILE, "w") as f:
             json.dump(seed_data, f, indent=4)

def load_skills():
      """Load skills from skills.md."""
      if os.path.exists(SKILLS_FILE):
         with open(SKILLS_FILE, "r") as f:
            return f.read()
      return "No skills information available."

def save_memory(role, content):
      """Save a message to memory with role, content, and timestamp."""
      memory = load_memory()
      timestamp = datetime.datetime.now().isoformat()
      memory.append({"role": role, "content": content, "timestamp": timestamp})
      with open(MEMORY_FILE, "w") as f:
         json.dump(memory, f, indent=4)

def search_memory(keyword):
      """Search memory for messages containing the keyword."""
      memory = load_memory()
      return [msg for msg in memory if keyword.lower() in msg["content"].lower()]

def get_recent_history(n=5):
      """Get the most recent n messages from memory."""
      memory = load_memory()
      return memory[-n:]

def build_messages(user_input):
      """Build the message list for the chatbot, including system prompt, recent history, and user input."""
      skills_profile = load_skills()

      relevant_memories = search_memory(user_input)
      memory_context = ""
      if relevant_memories:
         memory_context = "\nRelevant past memories found:\n" + "\n".join([f"- {m['role']}: {m['content']}" for m in relevant_memories])

      system_prompt = (
          "You are a helpful assistant.\n"
          f"Here is the learner's background profile:\n{skills_profile}\n"
          f"{memory_context}\n\n"
          "CRITICAL RULES:\n"
          "1. Use the provided memory and profile context to answer questions.\n"
          "2. Do not invent personal facts about the user.\n"
          "3. If the context/memory does not contain the answer, you MUST say 'I don't know.'\n"
      )

      recent_history = get_recent_history()
      messages = [{"role": "system", "content": system_prompt}]

      for msg in recent_history:
         messages.append({"role": msg["role"], "content": msg["content"]})

      messages.append({"role": "user", "content": user_input})
      return messages

def call_llm(messages, model):
    """Routes the prompt to the correct API based on the user's dropdown choice."""

    if model == "Groq":
         try:
            response = groq_client.chat.completions.create(
               model="llama-3.1-8b-instant",
               messages=messages
            )
            return response.choices[0].message.content
         except Exception as e:
            return f"Groq API Error: {str(e)}."
    elif model == "Gemini":
         try:
            gemini_prompt = ""
            for msg in messages:
                role_label = msg["role"].upper()
                gemini_prompt += f"{role_label}: {msg['content']}\n\n"

            response = gemini_client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=gemini_prompt
            )
            return response.text
         except Exception as e:
            return f"Gemini API Error: {str(e)}."
    else:
        return f"Error: Unknown model '{model}'. Please select a valid model."

def chat_bot(user_input, model):
      """Main chatbot function to handle user input and return AI response."""
      # Build messages for the model
      messages = build_messages(user_input)
      
      # Call the LLM with the constructed messages
      ai_response = call_llm(messages, model)
      
      # Save the user input and AI response to memory
      save_memory("user", user_input)
      save_memory("assistant", ai_response)
      
      return ai_response

def gradio_interface(message, history, model):
     return chat_bot(message, model)

def main():
      """Main function to run the chatbot interface."""
      init_memory()
      print("Booting up the Web UI...")

      with gradio.Blocks() as demo:
          gradio.Markdown("Day 4: Context-Aware Chatbot with Memory")
          chatbot_component = gradio.Chatbot(label="Chatbot")

          with gradio.Row():
              model_dropdown = gradio.Dropdown(
                  choices=["Groq", "Gemini"], 
                  value="Groq", 
                  show_label=False,
                  scale=1,
                  min_width=100
              )
              user_textbox = gradio.Textbox(
                  show_label=False, 
                  placeholder="Type your message here...", 
                  scale=8
              )
          
          def respond(message, history, model):
              """Handle the response from the chatbot and update the chat history."""
              if not message.strip():
                  yield "", history
                  return
              
              # Append the user's message to the history first
              history.append({"role": "user", "content": message})
              yield "", history
              
              # Call the chatbot function to get the AI response
              bot_message = chat_bot(message, model)
              history.append({"role": "assistant", "content": bot_message})
              yield "", history
          
          user_textbox.submit(
              fn=respond,
              inputs=[user_textbox, chatbot_component, model_dropdown],
              outputs=[user_textbox, chatbot_component]
          )

      demo.launch()

if __name__ == "__main__":
      main()