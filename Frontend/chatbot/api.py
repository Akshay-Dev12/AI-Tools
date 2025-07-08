import requests

def get_bot_response(user_input):
    response = requests.post("http://localhost:8000/chat", json={"prompt": user_input})
    return response.json()["response"]
