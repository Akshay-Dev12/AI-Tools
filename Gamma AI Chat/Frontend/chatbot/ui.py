import streamlit as st
from state import add_message, get_messages, clear_messages
from api import get_bot_response, clear_chat_history

def render_chat_interface():
    st.set_page_config(page_title="AI Chatbot", layout="centered")
    st.title("🤖 AI Gama")
    st.subheader("Powered by Seqato")

    if st.sidebar.button("Clear Chat"):
        if clear_chat_history():
            clear_messages()
            st.rerun()

    # Display chat messages from history on app rerun
    for message in get_messages():
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask something..."):
        # Add user message to chat history
        add_message("user", prompt)
        # Display user message in chat message container
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("bot", avatar="🤖"):
            with st.spinner("Thinking...."):
                response = get_bot_response(prompt)
                st.markdown(response)
        # Add assistant response to chat history
        add_message("bot", response)
