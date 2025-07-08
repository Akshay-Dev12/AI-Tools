import streamlit as st
from state import add_message, get_messages
from api import get_bot_response

def render_chat_interface():
    st.set_page_config(page_title="Local LLM Chat", layout="centered")
    st.title("💬 Chat with Local LLM (Ollama + FastAPI)")

    user_input = st.chat_input("Ask something...")

    if user_input:
        add_message("user", user_input)
        with st.spinner("Thinking..."):
            reply = get_bot_response(user_input)
        add_message("bot", reply)

    for msg in get_messages():
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
