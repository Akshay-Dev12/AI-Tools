from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, chat_history

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(chat_history.router)