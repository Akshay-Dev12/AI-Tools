# RAG Q&A Chatbot System

A complete Retrieval-Augmented Generation (RAG) application with FastAPI backend and Streamlit frontend for document-based question answering.

## 🌟 Features

- **Document Upload**: Support for PDF, DOCX, and TXT files
- **Intelligent Q&A**: Ask questions about your documents using natural language
- **Source Attribution**: See which document chunks were used for each answer
- **Vector Search**: ChromaDB for efficient semantic search
- **REST API**: FastAPI backend for scalability
- **Modern UI**: Beautiful Streamlit interface
- **Persistent Storage**: ChromaDB persists documents across sessions

## 📋 Prerequisites

- Python 3.8+
- Ollama (for local LLM) OR OpenAI API key
- 4GB+ RAM recommended

## 🚀 Installation

### 1. Clone or Create Project Directory

```bash
mkdir rag-chatbot
cd rag-chatbot
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama (Optional - for local LLM)

Visit [Ollama.ai](https://ollama.ai) and install Ollama, then:

```bash
ollama pull llama2
```

**Alternative**: Use OpenAI by modifying the LLM initialization in `main.py`:

```python
# Replace this line:
llm = Ollama(model="llama2", temperature=0.7)

# With this:
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key="your-key")
```

## 📁 Project Structure

```
rag-chatbot/
├── main.py              # FastAPI backend
├── app.py               # Streamlit frontend
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── chroma_db/          # ChromaDB storage (auto-created)
```

## 🎮 Usage

### Step 1: Start the FastAPI Backend

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Step 2: Start the Streamlit Frontend (New Terminal)

```bash
streamlit run app.py
```

The UI will open automatically at `http://localhost:8501`

### Step 3: Use the Application

1. **Upload Documents**: 
   - Click the file uploader in the sidebar
   - Select PDF, DOCX, or TXT files
   - Click "Upload Documents"

2. **Ask Questions**:
   - Type your question in the chat input
   - View the AI-generated answer
   - Check sources to see relevant document chunks

3. **Adjust Settings**:
   - Use the slider to control how many document chunks to retrieve
   - More chunks = more context but slower responses

4. **Clear Database**:
   - Click "Clear Database" to remove all uploaded documents

## 🔧 API Endpoints

### `GET /`
Health check endpoint

### `POST /upload`
Upload documents for processing
- **Body**: Form data with files
- **Returns**: Upload status and statistics

### `POST /query`
Query the document collection
- **Body**: `{"question": "your question", "top_k": 3}`
- **Returns**: Answer and source documents

### `GET /stats`
Get database statistics
- **Returns**: Document count and status

### `DELETE /clear`
Clear all documents from database

## 🎨 Customization

### Change Embedding Model

In `main.py`, modify:

```python
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"  # Better quality
)
```

### Change Chunk Size

In `main.py`, adjust:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Smaller chunks
    chunk_overlap=100,   # Less overlap
)
```

### Change LLM Provider

Replace Ollama with:

**OpenAI:**
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4", openai_api_key="sk-...")
```

**HuggingFace:**
```python
from langchain_community.llms import HuggingFaceHub
llm = HuggingFaceHub(repo_id="google/flan-t5-large", huggingfacehub_api_token="...")
```

## 🐛 Troubleshooting

### API Connection Error
- Ensure FastAPI is running on port 8000
- Check firewall settings

### Out of Memory
- Reduce chunk_size
- Use a smaller embedding model
- Process fewer documents at once

### Slow Responses
- Reduce top_k value
- Use a faster LLM
- Consider GPU acceleration for embeddings

### ChromaDB Errors
- Delete the `chroma_db` folder and restart
- Check write permissions

## 📊 Performance Tips

1. **Use GPU**: Install PyTorch with CUDA for faster embeddings
2. **Batch Processing**: Upload multiple documents at once
3. **Optimize Chunks**: Experiment with chunk_size and overlap
4. **Cache Results**: Implement caching for common queries
5. **Use Better Models**: GPT-4 or Claude for higher quality answers

## 🔒 Security Notes

- **Production**: Add authentication and rate limiting
- **API Keys**: Use environment variables, never hardcode
- **File Validation**: Implement size limits and virus scanning
- **CORS**: Restrict origins in production

## 📝 Environment Variables (Optional)

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_API_KEY=your_hf_key
API_HOST=0.0.0.0
API_PORT=8000
```

Load in `main.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

## 🤝 Contributing

Feel free to open issues or submit pull requests!

## 📄 License

MIT License - feel free to use for personal or commercial projects

## 🙏 Acknowledgments

- LangChain for the RAG framework
- ChromaDB for vector storage
- FastAPI for the backend
- Streamlit for the frontend
- HuggingFace for embeddings

---

**Need Help?** Open an issue or check the documentation for each component.