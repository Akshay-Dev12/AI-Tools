"""
Meeting Notes & Action Item Extractor - FastAPI backend
File: main.py

Features:
- POST /transcribe: upload an audio file (multipart/form-data) and receive:
    - transcript (text)
    - structured meeting notes (summary, key points)
    - action_items (list of tasks with optional assignee and due date when inferrable)
    - segments (optional segments with start/end timestamps)

- Uses Whisper (faster-whisper or openai/whisper) to transcribe audio.
- If OPENAI_API_KEY is provided, uses OpenAI Chat API to extract structured notes & tasks.
  Otherwise falls back to a local heuristic extractor (simple rules + regex).

How to run:
1. Create a virtualenv and install dependencies:
   pip install fastapi uvicorn python-multipart pydantic openai
   # optional (choose one):
   pip install faster-whisper
   # or
   pip install git+https://github.com/openai/whisper.git

2. Export OPENAI_API_KEY if you want LLM-based extraction (recommended for best quality):
   export OPENAI_API_KEY="sk-..."

3. Start server:
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Endpoints:
- GET /health
- POST /transcribe  (multipart: file: audio, optional: diarize (bool), language, model)

Example curl:
  curl -X POST "http://localhost:8000/transcribe" -F "file=@meeting.mp3" -F "language=en" -F "diarize=false"

Notes:
- This is a starting point. For production use, add authentication, rate-limiting, better diarization (pyannote), and persistent storage.
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import tempfile
import uuid
import logging
import re
import asyncio

# Optional imports for whisper
try:
    from faster_whisper import WhisperModel
    HAS_FASTER_WHISPER = True
except Exception:
    HAS_FASTER_WHISPER = False

# Optional fallback: openai/whisper local
try:
    import whisper as openai_whisper
    HAS_OPENAI_WHISPER = True
except Exception:
    HAS_OPENAI_WHISPER = False

# Optional OpenAI for structured extraction
try:
    import openai
    HAS_OPENAI = True
except Exception:
    HAS_OPENAI = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("meeting-extractor")

app = FastAPI(title="Meeting Notes & Action Item Extractor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global: whisper model (lazy)
_whisper_model = None


class ActionItem(BaseModel):
    task: str
    assignee: Optional[str] = None
    due: Optional[str] = None
    context: Optional[str] = None


class TranscriptionResult(BaseModel):
    transcript: str
    summary: str
    key_points: List[str]
    action_items: List[ActionItem]
    segments: Optional[List[Dict[str, Any]]] = None


@app.get("/health")
async def health():
    return {"status": "ok"}


async def load_whisper(model_name: str = "medium"):
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model

    if HAS_FASTER_WHISPER:
        logger.info("Loading faster-whisper model: %s", model_name)
        # device="cpu" or "cuda"
        model = WhisperModel(model_name, device="cpu", compute_type="int8")
        _whisper_model = ("faster", model)
        return _whisper_model

    if HAS_OPENAI_WHISPER:
        logger.info("Loading openai/whisper model: %s", model_name)
        model = openai_whisper.load_model(model_name)
        _whisper_model = ("openai", model)
        return _whisper_model

    raise RuntimeError("No whisper implementation available. Install faster-whisper or openai/whisper")


async def transcribe_with_whisper_local(filepath: str, language: Optional[str] = None, model_name: str = "medium", diarize: bool = False):
    """Transcribe audio using local whisper (faster-whisper preferred). Returns transcript and optional segments."""
    engine_type, model = await load_whisper(model_name)
    segments = []
    transcript_text = ""

    if engine_type == "faster":
        # faster-whisper API
        segments_gen, info = model.transcribe(filepath, beam_size=5, language=language)
        for seg in segments_gen:
            segments.append({
                "start": float(seg.start),
                "end": float(seg.end),
                "text": seg.text.strip(),
            })
            transcript_text += seg.text.strip() + " "

    else:
        # openai/whisper
        result = model.transcribe(filepath, language=language)
        # result['segments'] if available
        for seg in result.get("segments", []):
            segments.append({
                "start": float(seg.get("start", 0)),
                "end": float(seg.get("end", 0)),
                "text": seg.get("text", "").strip(),
            })
            transcript_text += seg.get("text", "").strip() + " "

    transcript_text = transcript_text.strip()
    return transcript_text, segments


async def extract_structured_with_openai(transcript: str) -> Dict[str, Any]:
    """Use OpenAI Chat API to extract summary, key points, and action items."""
    if not HAS_OPENAI or not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OpenAI API not configured")

    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = f"""
You are an assistant that extracts structured meeting notes from a meeting transcript.
Given the transcript below, produce a JSON object with fields:
- summary: 2-4 sentence concise summary
- key_points: array of 3-8 bullet points (short phrases)
- action_items: array of objects with fields: task, assignee (optional), due (optional), context (optional)
The transcript:
---
{transcript}
---
Return only valid JSON.
"""

    # ChatCompletion with gpt-4o or gpt-4; fall back safely
    try:
        response = openai.ChatCompletion.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=700,
        )
        content = response["choices"][0]["message"]["content"]
    except Exception as e:
        # try completions
        logger.warning("ChatCompletion failed: %s", e)
        response = openai.Completion.create(
            model=os.getenv("OPENAI_MODEL", "text-davinci-003"),
            prompt=prompt,
            temperature=0.0,
            max_tokens=700,
        )
        content = response["choices"][0]["text"]

    # Attempt to find JSON in content
    json_text = extract_json_block(content)
    if not json_text:
        # if cannot parse, wrap in fallback
        raise RuntimeError("OpenAI did not return JSON or parsing failed. Response: " + content[:1000])

    import json
    parsed = json.loads(json_text)
    return parsed


def extract_json_block(text: str) -> Optional[str]:
    """Extract the first JSON object or array from a string."""
    # naive approach: find first { and last matching }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    # try array
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return None


def heuristic_extract(transcript: str) -> Dict[str, Any]:
    """A simple rule-based extractor for summary, key points and action items."""
    # split into sentences (very naive)
    sentences = re.split(r"(?<=[.!?])\s+", transcript)
    # summary: first 2 sentences (fallback)
    summary = " ".join(sentences[:2]).strip()

    # key points: pick sentences that are short and contain keywords or are likely important
    keywords = ["decide", "decided", "decision", "plan", "problem", "risk", "next", "update", "deadline"]
    key_points = []
    for s in sentences:
        sl = s.lower()
        if len(s) < 250 and any(k in sl for k in keywords):
            key_points.append(s.strip())
    # if none found, pick top 4 non-empty sentences
    if not key_points:
        key_points = [s.strip() for s in sentences if s.strip()][:4]

    # action items: find lines with 'action', 'todo', 'follow up', or imperatives + names
    action_patterns = [r"todo[:\-]?\s*(.*)", r"action[:\-]?\s*(.*)", r"follow up with (.*?)[:\-]?(.*)", r"(?i)(assign|will|we will|please|please\s+check)\s+(.*)"]
    action_items = []
    for s in sentences:
        for pat in action_patterns:
            m = re.search(pat, s, flags=re.IGNORECASE)
            if m:
                # build a simple task
                task_text = (m.group(1) if m.groups() else s).strip()
                if not task_text:
                    task_text = s.strip()
                # try to infer assignee by looking for capitalized names or patterns
                assignee = None
                name_m = re.search(r"([A-Z][a-z]+)\s*(?:will|to|:\s)", s)
                if name_m:
                    assignee = name_m.group(1)
                action_items.append({"task": task_text, "assignee": assignee, "due": None, "context": s.strip()})

    # also look for lines like "Alice: I'll take X"
    for s in sentences:
        colon = s.split(":", 1)
        if len(colon) == 2 and len(colon[0].split()) <= 3:  # likely a speaker
            speaker = colon[0].strip()
            body = colon[1].strip()
            if re.search(r"(I'll|I will|I'll take|I'll do|I will take|assign|take care|action)", body, flags=re.IGNORECASE):
                action_items.append({"task": body, "assignee": speaker, "due": None, "context": s.strip()})

    # dedupe
    seen = set()
    unique_actions = []
    for a in action_items:
        key = a["task"]
        if key not in seen:
            seen.add(key)
            unique_actions.append(a)

    # format
    action_items = unique_actions

    return {
        "summary": summary,
        "key_points": key_points,
        "action_items": action_items,
    }


@app.post("/transcribe", response_model=TranscriptionResult)
async def transcribe_endpoint(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    diarize: Optional[bool] = Form(False),
    model_name: Optional[str] = Form("medium"),
    use_llm: Optional[bool] = Form(True),
):
    # save uploaded file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    suffix = os.path.splitext(file.filename)[1]
    tmpdir = tempfile.mkdtemp(prefix="meet-")
    filename = os.path.join(tmpdir, f"{uuid.uuid4().hex}{suffix}")

    with open(filename, "wb") as f:
        content = await file.read()
        f.write(content)

    logger.info("Saved uploaded file to %s", filename)

    try:
        transcript, segments = await transcribe_with_whisper_local(filename, language=language, model_name=model_name, diarize=diarize)
    except Exception as e:
        logger.exception("Transcription failed")
        raise HTTPException(status_code=500, detail=str(e))

    # Post-process: use LLM if configured and requested
    structured = None
    if use_llm and HAS_OPENAI and os.getenv("OPENAI_API_KEY"):
        try:
            structured = await extract_structured_with_openai(transcript)
        except Exception as e:
            logger.warning("OpenAI extraction failed: %s", e)
            structured = heuristic_extract(transcript)
    else:
        structured = heuristic_extract(transcript)

    # Build response
    action_items_parsed = []
    for a in structured.get("action_items", []):
        action_items_parsed.append(ActionItem(
            task=a.get("task") if isinstance(a, dict) else str(a),
            assignee=a.get("assignee") if isinstance(a, dict) else None,
            due=a.get("due") if isinstance(a, dict) else None,
            context=a.get("context") if isinstance(a, dict) else None,
        ))

    # ensure key_points is list[str]
    key_points = structured.get("key_points") or []
    if isinstance(key_points, str):
        key_points = [key_points]

    result = TranscriptionResult(
        transcript=transcript,
        summary=structured.get("summary", ""),
        key_points=key_points,
        action_items=action_items_parsed,
        segments=segments,
    )

    # cleanup file (optional)
    try:
        os.remove(filename)
    except Exception:
        pass

    return JSONResponse(content=result.dict())


# If run as script
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)