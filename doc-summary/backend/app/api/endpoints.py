from fastapi import APIRouter, HTTPException
from app.schemas.summary import SummaryRequest, SummaryResponse
from app.services.summarizer_service import summarize_text, extract_keywords

router = APIRouter()


@router.post("/summarize", response_model=SummaryResponse)
async def summarize(req: SummaryRequest) -> SummaryResponse:
    """
    Endpoint to receive text and return a summary and keywords.
    """
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    try:
        print(f"Request received to process text with summary length: {req.summary_length}")
        summary = summarize_text(req.text, req.summary_length)
        keywords = extract_keywords(req.text)
        return SummaryResponse(summary=summary, keywords=keywords)
    except Exception as e:
        # Log the exception here if logging is set up
        raise HTTPException(
            status_code=500, detail=f"An error occurred during processing: {e}"
        )