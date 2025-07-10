import json
from app.core import constants

def get_chat_history():
    try:
        with open(constants.CHAT_HISTORY_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_chat_history(history):
    with open(constants.CHAT_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)
