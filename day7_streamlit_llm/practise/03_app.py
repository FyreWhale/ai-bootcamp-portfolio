import streamlit as st
import config
from services.gemini_service import get_ai_response_stream, parse_stream_chunks

st.set_page_config(page_title="Ollama Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 Local Ollama Chatbot")
st.caption(f"Running locally with model: **{config.MODEL_NAME}**")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = [{'role': 'system', 'content': config.SYSTEM_PROMPT}]

for msg in st.session_state.messages:
    if msg['role'] != 'system':
        with st.chat_message(msg['role']):
            st.write(msg['content'])

if user_input := st.chat_input("Type your question here..."):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({'role': 'user', 'content': user_input})

    with st.chat_message("assistant"):
        try:
            raw_stream = get_ai_response_stream(st.session_state.messages)
            clean_text_stream = parse_stream_chunks(raw_stream)
            full_response = st.write_stream(clean_text_stream)
            st.session_state.messages.append({'role': 'assistant', 'content': full_response})
        except Exception as e:
            st.error(f"Error communicating with backend: {e}")
            st.info("Ensure Ollama is running locally via `ollama serve` in your terminal.")