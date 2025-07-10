from transformers import pipeline
import yake
from typing import List

# Initialize the summarizer pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Keyword extraction settings
keyword_extractor = yake.KeywordExtractor(
    lan="en", n=1, dedupLim=0.9, dedupFunc="seqm", windowsSize=1, top=10, features=None
)


def extract_keywords(text: str) -> List[str]:
    """
    Extracts the top keywords from the given text.
    """
    keywords = keyword_extractor.extract_keywords(text)
    return [kw for kw, score in keywords]


def summarize_text(
    text: str, summary_length: str = "medium", max_chunk: int = 500
) -> str:
    """
    Summarizes the given text based on the desired length.
    """
    length_multipliers = {
        "short": {"max_ratio": 0.3, "min_ratio": 0.1},
        "medium": {"max_ratio": 0.5, "min_ratio": 0.2},
        "long": {"max_ratio": 0.7, "min_ratio": 0.4},
    }

    ratios = length_multipliers.get(summary_length, length_multipliers["medium"])
    max_ratio = ratios["max_ratio"]
    min_ratio = ratios["min_ratio"]

    sentences = text.splitlines()
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 < max_chunk:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    summary_parts = []
    for chunk in chunks:
        if not chunk:
            continue

        token_len = len(chunk.split())

        # Define dynamic max and min length for the summary
        max_len = min(150, int(token_len * max_ratio))
        min_len = max(30, int(token_len * min_ratio))

        if min_len > max_len:
            min_len = max_len // 2

        result = summarizer(
            chunk, max_length=max_len, min_length=min_len, do_sample=False
        )
        if result and isinstance(result, list):
            summary_parts.append(result[0]["summary_text"])

    return " ".join(summary_parts).strip()