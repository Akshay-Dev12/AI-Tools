# AI Tools Repository

This repository is a collection of AI-powered applications and Python scripts, showcasing various machine learning and web development concepts.

## Projects

### 1. Gamma AI Chat

A real-time chat application that uses a large language model to generate responses.

**Features:**

*   Real-time chat interface
*   Chat history persistence
*   Powered by the Ollama language model
*   Backend built with FastAPI
*   Frontend built with Streamlit

**Technologies Used:**

*   **Backend:** Python, FastAPI, Uvicorn
*   **Frontend:** Python, Streamlit
*   **ML Model:** Ollama

**How to Run:**

1.  **Run the Backend:**
    ```bash
    cd "Gamma AI Chat/Backend/chatbot"
    pip install -r requirements.txt
    uvicorn app.main:app --reload
    ```

2.  **Run the Frontend:**
    ```bash
    cd "Gamma AI Chat/Frontend/chatbot"
    pip install -r requirements.txt
    streamlit run app.py
    ```

### 2. Gamma Doc Summary

A web application that summarizes the content of PDF documents.

**Features:**

*   PDF document upload
*   Text extraction from PDFs
*   Text summarization using a pre-trained model
*   Keyword extraction
*   Backend built with FastAPI
*   Frontend built with Streamlit

**Technologies Used:**

*   **Backend:** Python, FastAPI, Uvicorn, `transformers`, `yake`
*   **Frontend:** Python, Streamlit, `PyPDF2`
*   **ML Model:** `facebook/bart-large-cnn`

**How to Run:**

1.  **Run the Backend:**
    ```bash
    cd "Gamma Doc Summary/backend"
    pip install -r requirements.txt
    uvicorn main:app --reload
    ```

2.  **Run the Frontend:**
    ```bash
    cd "Gamma Doc Summary/frontend"
    pip install -r requirements.txt
    streamlit run app.py
    ```

### 3. FastAPI Examples

A collection of Python scripts demonstrating various features of the FastAPI framework.

**Features:**

*   Basic CRUD operations
*   Background tasks
*   WebSocket communication
*   Dependency injection
