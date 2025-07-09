import streamlit as st
from api import get_chat_history

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        history = get_chat_history()
        for message in history:
            role = message["role"]
            if role == "assistant":
                role = "bot"
            add_message(role, message["content"])

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def get_messages():
    return st.session_state.messages

def clear_messages():
    st.session_state.messages = []
