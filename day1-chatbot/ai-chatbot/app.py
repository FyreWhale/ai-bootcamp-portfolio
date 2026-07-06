import streamlit as st
from chatbot import chat

st.title("Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_prompt := st.chat_input("Type your message here..."):
    with st.chat_message("user"):
        st.markdown(user_prompt)

    response = chat(user_prompt, st.session_state.messages)

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "user", "content": user_prompt})
    st.session_state.messages.append({"role": "assistant", "content": response})