from state import initialize_session_state
from ui import render_chat_interface

def main():
    initialize_session_state()
    render_chat_interface()

if __name__ == "__main__":
    main()