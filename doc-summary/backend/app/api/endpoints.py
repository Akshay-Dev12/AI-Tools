from fastapi import APIRouter, HTTPException
from app.schemas.summary import SummaryRequest, SummaryResponse
from app.services.summarizer_service import summarize_text

router = APIRouter()

@router.post("/summarize", response_model=SummaryResponse)
async def summarize(req: SummaryRequest) -> SummaryResponse:
    """
    Endpoint to receive text and return a summary.
    """
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    
    try:
        print("Request received to process text")
        summary = summarize_text(req.text)
        return SummaryResponse(summary=summary)
    except Exception as e:
        # Log the exception here if logging is set up
        raise HTTPException(status_code=500, detail=f"An error occurred during summarization: {e}")
