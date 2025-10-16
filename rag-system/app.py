import streamlit as st
import requests
from typing import List
import time

# Configuration
API_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="RAG Q&A Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1E88E5;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    .bot-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'documents_uploaded' not in st.session_state:
    st.session_state.documents_uploaded = False

def check_api_status():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/")
        return response.status_code == 200
    except:
        return False

def upload_documents(files):
    """Upload documents to the API"""
    files_data = []
    for file in files:
        files_data.append(('files', (file.name, file.getvalue(), file.type)))
    
    try:
        response = requests.post(f"{API_URL}/upload", files=files_data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def query_documents(question: str, top_k: int = 3):
    """Query the documents"""
    try:
        response = requests.post(
            f"{API_URL}/query",
            json={"question": question, "top_k": top_k}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_stats():
    """Get database statistics"""
    try:
        response = requests.get(f"{API_URL}/stats")
        return response.json()
    except:
        return {"document_count": 0, "status": "unavailable"}

def clear_database():
    """Clear all documents"""
    try:
        response = requests.delete(f"{API_URL}/clear")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Main UI
st.markdown('<p class="main-header">🤖 RAG Q&A Chatbot</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📚 Document Management")
    
    # API Status
    api_status = check_api_status()
    if api_status:
        st.success("✅ API Connected")
    else:
        st.error("❌ API Disconnected")
        st.warning("Please ensure FastAPI backend is running on port 8000")
    
    # Stats
    if api_status:
        stats = get_stats()
        st.metric("Documents in Database", stats.get('document_count', 0))
    
    st.divider()
    
    # File Upload
    st.subheader("Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Upload PDF, DOCX, or TXT files"
    )
    
    if uploaded_files and st.button("📤 Upload Documents", type="primary"):
        with st.spinner("Processing documents..."):
            result = upload_documents(uploaded_files)
            
            if 'error' in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success(f"✅ {result.get('message', 'Upload successful')}")
                st.info(f"Files processed: {result.get('files_processed', 0)}")
                st.info(f"Chunks created: {result.get('chunks_created', 0)}")
                st.session_state.documents_uploaded = True
                time.sleep(1)
                st.rerun()
    
    st.divider()
    
    # Settings
    st.subheader("⚙️ Settings")
    top_k = st.slider("Number of relevant chunks", 1, 10, 3)
    
    st.divider()
    
    # Clear Database
    if st.button("🗑️ Clear Database", type="secondary"):
        if st.session_state.documents_uploaded:
            result = clear_database()
            if 'error' not in result:
                st.success("Database cleared!")
                st.session_state.messages = []
                st.session_state.documents_uploaded = False
                time.sleep(1)
                st.rerun()
    
    st.divider()
    
    # Instructions
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        1. **Upload Documents**: Use the file uploader to add PDF, DOCX, or TXT files
        2. **Ask Questions**: Type your questions in the chat below
        3. **View Sources**: See which document chunks were used for each answer
        4. **Adjust Settings**: Change the number of relevant chunks to retrieve
        5. **Clear Database**: Remove all documents when done
        """)

# Main chat interface
if not api_status:
    st.error("⚠️ Cannot connect to API. Please start the FastAPI backend first.")
    st.code("uvicorn main:app --reload", language="bash")
else:
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message">👤 <strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot-message">🤖 <strong>Assistant:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            
            # Show sources if available
            if "sources" in message and message["sources"]:
                with st.expander("📄 View Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f'<div class="source-box">', unsafe_allow_html=True)
                        st.markdown(f"**Source {i}:** {source['metadata'].get('source', 'Unknown')}")
                        st.markdown(f"**Chunk:** {source['metadata'].get('chunk_id', 'N/A')}")
                        st.text_area(f"Content {i}", source['content'], height=100, disabled=True, key=f"source_{i}_{message.get('timestamp', '')}")
                        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        if not st.session_state.documents_uploaded:
            st.warning("⚠️ Please upload documents first before asking questions!")
        else:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            st.markdown(f'<div class="chat-message user-message">👤 <strong>You:</strong> {prompt}</div>', unsafe_allow_html=True)
            
            # Get response
            with st.spinner("Thinking..."):
                response = query_documents(prompt, top_k)
                
                if 'error' in response:
                    bot_message = f"Sorry, I encountered an error: {response['error']}"
                    st.session_state.messages.append({"role": "assistant", "content": bot_message})
                else:
                    bot_message = response.get('answer', 'No answer available')
                    sources = response.get('sources', [])
                    timestamp = response.get('timestamp', '')
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": bot_message,
                        "sources": sources,
                        "timestamp": timestamp
                    })
            
            st.rerun()
    
    # Show welcome message if no messages
    if len(st.session_state.messages) == 0:
        st.info("👋 Welcome! Upload documents and start asking questions!")

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        Built with LangChain, ChromaDB, FastAPI & Streamlit | 
        <a href='https://github.com' target='_blank'>GitHub</a>
    </div>
""", unsafe_allow_html=True)