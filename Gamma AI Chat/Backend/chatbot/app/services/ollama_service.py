import httpx
from app.core.config import OLLAMA_URL
from app.core.constants import INTERNAL_SERVER_ERROR, TIME_OUT_OLLAMA_MSSG, OLLAMA_TIME_OUT, MODEL, OLLAMA_STREAM, STREAM, PROMPT

async def get_ollama_response(model: str, messages: list, prompt: str):
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIME_OUT) as client:
            response = await client.post(
                OLLAMA_URL,
                json={MODEL: model, PROMPT: prompt, STREAM: OLLAMA_STREAM}
            )
        response_data = response.json()
        print("Get ollama response service completed.")
        return response_data
    except httpx.ReadTimeout:
        return {TIME_OUT_OLLAMA_MSSG}
    except Exception as e:
        print("Exception occured at get ollama response service: "+e)
        return {INTERNAL_SERVER_ERROR}
