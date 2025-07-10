from transformers import pipeline

# Initialize the summarizer pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text: str, max_chunk: int = 500) -> str:
    """
    Summarizes the given text by splitting it into chunks and processing each chunk.
    """
    # Using splitlines() is often more robust than splitting on ". "
    sentences = text.splitlines()
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # Check if adding the next sentence exceeds the chunk size
        if len(current_chunk) + len(sentence) + 1 < max_chunk:
            current_chunk += sentence + " "
        else:
            # Add the completed chunk to the list
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Start a new chunk with the current sentence
            current_chunk = sentence + " "
    
    # Add the last remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    summary_parts = []
    for chunk in chunks:
        if not chunk:
            continue
        
        token_len = len(chunk.split())
        # Define dynamic max and min length for the summary
        max_len = min(130, int(token_len * 0.7))
        min_len = max(20, int(token_len * 0.3))

        # Ensure min_len is not greater than max_len
        if min_len > max_len:
            min_len = max_len // 2

        # Generate summary for the chunk
        result = summarizer(
            chunk, 
            max_length=max_len, 
            min_length=min_len, 
            do_sample=False
        )
        if result and isinstance(result, list):
            summary_parts.append(result[0]["summary_text"])

    return " ".join(summary_parts).strip()
