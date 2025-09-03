from fastapi import APIRouter, Form, UploadFile, File
from app.services.ollama_service import get_ollama_response
from app.services.chat_history_service import get_chat_history, save_chat_history
from app.core import config, constants
import base64

router = APIRouter()

@router.post(constants.CHAT_ROUTE_URL)
async def chat_with_ollama(prompt: str = Form(...), image: UploadFile = File(None)):
    model = config.OLLAMA_MODEL
    
    history = get_chat_history()
    history.append({"role": "user", "content": prompt})
    print("Prompt: "+prompt)
    
    image_b64 = None
    if image:
        contents = await image.read()
        image_b64 = base64.b64encode(contents).decode("utf-8")
    
    response = await get_ollama_response(model, history, prompt, image=image_b64)
    
    history.append({"role": "assistant", "content": response["response"]})
    save_chat_history(history)
    
    return response