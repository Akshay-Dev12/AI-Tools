from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from summarizer import summarize_text

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummaryRequest(BaseModel):
    text: str

@app.post("/summarize")
async def summarize(req: SummaryRequest):
    if not req.text.strip():
        return {"summary": "⚠️ No input text."}
    
    summary = summarize_text(req.text)
    return {"summary": summary}
