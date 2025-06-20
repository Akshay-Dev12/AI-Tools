from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# curl http://localhost:11434/api/generate -d "{ \"model\": \"mistral\", \"prompt\": \"Who are you?\" }" - CMD ollama Test
# uvicorn main:app --reload - backend
# streamlit run app.py - frontend

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"

@app.post("/chat")
async def chat_with_ollama(request: Request):
    body = await request.json()
    prompt = body.get("prompt")
    model = body.get("model", "mistral")
    print("Chat API receive: "+ prompt + model)

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json={"model": model, "prompt": prompt, "stream": False}
            )
        response_data = response.json()
        return {"response": response_data.get("response", "")}
    except httpx.ReadTimeout:
        return {"response": "⚠️ Error: Timed out waiting for Ollama to respond."}
    except Exception as e:
        return {"response": f"⚠️ Unexpected error: {str(e)}"}
    

