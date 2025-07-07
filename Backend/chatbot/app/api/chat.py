from fastapi import APIRouter, Request
from app.services.ollama_service import get_ollama_response
from app.core import config, constants

router = APIRouter()

@router.post(constants.CHAT_ROUTE_URL)
async def chat_with_ollama(request: Request):
    body = await request.json()
    prompt = body.get(constants.PROMPT)
    model = body.get(constants.MODEL, config.OLLAMA_MODEL)
    print("Chat API receive: "+ prompt + model)
    return await get_ollama_response(model, prompt)