"""
BOT2MX4 - Servidor principal multi-cliente
"""

import os
import asyncio
from fastapi import FastAPI, Request, Response
from dotenv import load_dotenv
from app.brain import get_response, clear_history
from app.messenger import send_message, send_typing

load_dotenv()

app = FastAPI(title="Bot2MX4", version="2.0.0")

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "bot2mx4_secret_2024")


@app.get("/")
async def root():
    return {"status": "✅ Bot2MX4 activo", "version": "2.0.0"}


@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    mode      = params.get("hub.mode")
    token     = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(status_code=403)


@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()

    if body.get("object") != "page":
        return {"status": "ignored"}

    for entry in body.get("entry", []):
        page_id = str(entry.get("id", ""))

        for event in entry.get("messaging", []):
            sender_id = event.get("sender", {}).get("id")
            message   = event.get("message", {})

            if not message or "text" not in message:
                continue

            user_text = message["text"].strip()
            print(f"[PÁGINA {page_id}] Usuario {sender_id}: {user_text}")

            if user_text.lower() in ["reiniciar", "reset"]:
                clear_history(sender_id)
                send_message(sender_id, "¡Listo! Empecemos de nuevo 😊", page_id)
                continue

            send_typing(sender_id, page_id)

            loop = asyncio.get_event_loop()
            bot_reply = await loop.run_in_executor(
                None, get_response, sender_id, user_text, page_id
            )

            send_message(sender_id, bot_reply, page_id)

    return {"status": "ok"}
