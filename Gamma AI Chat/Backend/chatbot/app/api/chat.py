from fastapi import APIRouter, Request
from app.services.ollama_service import get_ollama_response
from app.services.chat_history_service import get_chat_history, save_chat_history
from app.core import config, constants

router = APIRouter()

@router.post(constants.CHAT_ROUTE_URL)
async def chat_with_ollama(request: Request):
    body = await request.json()
    prompt = body.get(constants.PROMPT)
    model = body.get(constants.MODEL, config.OLLAMA_MODEL)
    
    history = get_chat_history()
    history.append({"role": "user", "content": prompt})
    print("Prompt: "+prompt)
    
    response = await get_ollama_response(model, history, prompt)
    
    history.append({"role": "assistant", "content": response["response"]})
    save_chat_history(history)
    
    return response