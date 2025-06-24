from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text, max_chunk=500):
    sentences = text.split(". ")
    chunks = []
    chunk = ""

    for sentence in sentences:
        if len(chunk) + len(sentence) < max_chunk:
            chunk += sentence + ". "
        else:
            chunks.append(chunk.strip())
            chunk = sentence + ". "
    chunks.append(chunk.strip())

    summary = ""
    for chunk in chunks:
        token_len = len(chunk.split())
        max_len = min(130, int(token_len * 0.7))
        min_len = max(20, int(token_len * 0.3))
        result = summarizer(chunk, max_length=max_len, min_length=min_len, do_sample=False)[0]
        summary += result["summary_text"] + " "
    return summary.strip()