# Global News Topic Tracker

This project scrapes Google News and summarizes trending topics using local Large Language Models (LLMs) through Ollama. It features a FastAPI backend for data processing and a Streamlit frontend for user interaction.

## Features

- **Google News Scraping**: Fetches news headlines from Google News RSS feeds based on country, language, topic, or search query.
- **LLM Summarization**: Utilizes local LLMs via Ollama to generate summaries of news headlines.
- **Real-time Streaming**: Supports streaming responses for summaries to provide a more interactive user experience.
- **News Analytics**: Provides basic analytics on news headlines, including top keywords and source distribution.
- **Interactive UI**: A web interface built with Streamlit allows users to easily filter news and view summaries and analytics.
- **Customizable**: Easily configure the LLM models used for summarization (e.g., speed vs. quality).

## Project Structure

-   `backend`: Contains the FastAPI application that handles news scraping, interacts with the Ollama server for summarization, and provides API endpoints.
-   `frontend`: Contains the Streamlit web application that serves as the user interface for the project.
-   `llm`: Contains a standalone script using Langchain and Ollama for summarizing content from a URL. Note: This is not directly used by the main application.

## How to run

### Prerequisites

-   Python 3.8+
-   [Ollama](https://ollama.ai/) installed and running. You need to have models available, for example:
    ```bash
    ollama pull llama3.2:1b
    ollama pull qwen2:7b
    ```

### 1. Installation

Install the required Python packages for each part of the project:

```bash
# For the backend
pip install -r backend/requirements.txt

# For the frontend
pip install -r frontend/requirements.txt

# For the standalone llm script (optional)
pip install -r llm/requirements.txt
```

### 2. Run the Backend

The backend server is built with FastAPI.

```bash
uvicorn backend.main:app --reload --port 8005
```

The API will be available at `http://localhost:8005`.

### 3. Run the Frontend

The frontend is a Streamlit application.

```bash
streamlit run frontend/app.py
```

The application will be accessible in your browser, typically at `http://localhost:8501`.

## API Endpoints

The FastAPI backend provides the following endpoints:

-   `GET /scrape_news`: Scrapes news from Google News.
    -   **Query Params**: `section`, `query`, `country`, `language`, `limit`.
-   `POST /summarize`: Generates a summary for a list of texts.
    -   **Body**: `{ "texts": ["headline1", "headline2"], "model": "llama3.2:1b", "stream": false }`
-   `GET /news_analytics`: Provides analytics on news headlines.
    -   **Query Params**: `section`, `query`, `country`, `language`, `limit`.
-   `GET /available_countries`: Returns a list of supported countries.
-   `GET /available_languages`: Returns a list of supported languages.
-   `GET /models`: Returns a list of recommended LLM models for different use cases.
