import streamlit as st
import requests

st.set_page_config(page_title="Local LLM Chat", layout="centered")
st.title("💬 Chat with Local LLM (Ollama + FastAPI)")

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Thinking..."):
        response = requests.post("http://localhost:8000/chat", json={"prompt": user_input})
        reply = response.json()["response"]
        st.session_state.messages.append({"role": "bot", "content": reply})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
