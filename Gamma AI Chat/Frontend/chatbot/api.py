import requests

BACKEND_URL = "http://localhost:8000"

def get_bot_response(user_input):
    response = requests.post(BACKEND_URL+"/chat", json={"prompt": user_input})
    return response.json()["response"]

def get_chat_history():
    response = requests.get(BACKEND_URL+"/chat-history")
    return response.json()

def clear_chat_history():
    response = requests.post(BACKEND_URL+"/clear-chat")
    return response.ok
