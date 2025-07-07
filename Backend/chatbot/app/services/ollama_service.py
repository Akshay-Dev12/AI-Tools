import httpx
from app.core.config import OLLAMA_URL
from app.core.constants import INTERNAL_SERVER_ERROR, TIME_OUT_OLLAMA_MSSG, OLLAMA_TIME_OUT, MODEL, PROMPT, OLLAMA_STREAM, STREAM

async def get_ollama_response(model: str, prompt: str):
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIME_OUT) as client:
            response = await client.post(
                OLLAMA_URL,
                json={MODEL: model, PROMPT: prompt, STREAM: OLLAMA_STREAM}
            )
        response_data = response.json()
        print("Get ollama response service completed.")
        return {"response": response_data.get("response", "")}
    except httpx.ReadTimeout:
        return {TIME_OUT_OLLAMA_MSSG}
    except Exception as e:
        print("Exception occured at get ollama response service: "+e)
        return {INTERNAL_SERVER_ERROR}
