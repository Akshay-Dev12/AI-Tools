from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import PyPDF2
import docx
import io
import os
from datetime import datetime

app = FastAPI(title="RAG Q&A API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ChromaDB setup
CHROMA_PATH = "./chroma_db"
client = chromadb.PersistentClient(path=CHROMA_PATH)

# Global vectorstore
vectorstore = None

class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

class QuestionResponse(BaseModel):
    answer: str
    sources: List[dict]
    timestamp: str

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    doc = docx.Document(io.BytesIO(file_content))
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file"""
    return file_content.decode('utf-8')

@app.get("/")
async def root():
    return {"message": "RAG Q&A API is running", "status": "active"}

@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process documents"""
    global vectorstore
    
    try:
        all_texts = []
        metadata_list = []
        
        for file in files:
            content = await file.read()
            filename = file.filename
            
            # Extract text based on file type
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(content)
            elif filename.endswith('.docx'):
                text = extract_text_from_docx(content)
            elif filename.endswith('.txt'):
                text = extract_text_from_txt(content)
            else:
                continue
            
            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            chunks = text_splitter.split_text(text)
            
            # Add chunks with metadata
            for i, chunk in enumerate(chunks):
                all_texts.append(chunk)
                metadata_list.append({
                    "source": filename,
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                })
        
        if not all_texts:
            raise HTTPException(status_code=400, detail="No valid documents found")
        
        # Create or update vectorstore
        if vectorstore is None:
            vectorstore = Chroma.from_texts(
                texts=all_texts,
                embedding=embeddings,
                metadatas=metadata_list,
                persist_directory=CHROMA_PATH,
                collection_name="documents"
            )
        else:
            vectorstore.add_texts(
                texts=all_texts,
                metadatas=metadata_list
            )
        
        return {
            "message": "Documents uploaded successfully",
            "files_processed": len(files),
            "chunks_created": len(all_texts)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

@app.post("/query", response_model=QuestionResponse)
async def query_documents(request: QuestionRequest):
    """Query the document collection"""
    global vectorstore
    
    if vectorstore is None:
        raise HTTPException(status_code=400, detail="No documents uploaded yet")
    
    try:
        # Retrieve relevant documents
        retriever = vectorstore.as_retriever(
            search_kwargs={"k": request.top_k}
        )
        
        # Create prompt template
        template = """Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context: {context}
        
        Question: {question}
        
        Answer: """
        
        QA_PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Initialize LLM (using Ollama - you can switch to OpenAI or other providers)
        llm = Ollama(model="llama2", temperature=0.7)
        
        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": QA_PROMPT}
        )
        
        # Get answer
        result = qa_chain({"query": request.question})
        
        # Format sources
        sources = []
        for doc in result['source_documents']:
            sources.append({
                "content": doc.page_content[:200] + "...",
                "metadata": doc.metadata
            })
        
        return QuestionResponse(
            answer=result['result'],
            sources=sources,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying documents: {str(e)}")

@app.delete("/clear")
async def clear_database():
    """Clear all documents from the database"""
    global vectorstore
    
    try:
        if os.path.exists(CHROMA_PATH):
            import shutil
            shutil.rmtree(CHROMA_PATH)
        
        vectorstore = None
        
        return {"message": "Database cleared successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    global vectorstore
    
    if vectorstore is None:
        return {"document_count": 0, "status": "empty"}
    
    try:
        collection = vectorstore._collection
        count = collection.count()
        
        return {
            "document_count": count,
            "status": "active"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)