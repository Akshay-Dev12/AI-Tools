from fastapi import APIRouter
from app.core import constants
from app.services.chat_history_service import save_chat_history, get_chat_history

router = APIRouter()

@router.post(constants.CLEAR_CHAT_ROUTE_URL)
async def clear_chat():
    save_chat_history([])
    return {"message": "Chat history cleared."}

@router.get(constants.GET_CHAT_HISTORY_ROUTE_URL)
async def get_history():
    return get_chat_history()