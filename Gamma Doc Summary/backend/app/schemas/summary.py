from pydantic import BaseModel, Field
from typing import List


class SummaryRequest(BaseModel):
    text: str
    summary_length: str = Field(
        "medium", description="Desired summary length: short, medium, or long"
    )


class SummaryResponse(BaseModel):
    summary: str
    keywords: List[str]