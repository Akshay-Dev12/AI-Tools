# Global News Topic Tracker

This project scrapes Google News and summarizes trending topics using LLMs.

## Project Structure

- `backend`: Contains the FastAPI backend that serves the summarization model.
- `frontend`: Contains the Streamlit frontend for user interaction.
- `llm`: Contains the Langchain and Ollama client for summarization.

## How to run

1.  Install the requirements for each directory:
    ```
    pip install -r backend/requirements.txt
    pip install -r frontend/requirements.txt
    pip install -r llm/requirements.txt
    ```
2.  Run the backend:
    ```
    uvicorn backend.main:app --reload
    ```
3.  Run the frontend:
    ```
    streamlit run frontend/app.py
    ```
