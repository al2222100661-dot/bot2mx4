"""
BOT2MX4 - Servidor principal multi-cliente
"""

import os
import asyncio
from fastapi import FastAPI, Request, Response, BackgroundTasks
from dotenv import load_dotenv
from app.brain import get_response, clear_history
from app.messenger import send_message, send_typing

load_dotenv()

app = FastAPI(title="Bot2MX4", version="2.0.0")

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "bot2mx4_secret_2024")

mensajes_procesados = set()


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


def procesar_evento(sender_id, user_text, page_id):
    """Esta función corre en segundo plano, no bloquea la respuesta a Facebook."""
    if user_text.lower() in ["reiniciar", "reset"]:
        clear_history(sender_id)
        send_message(sender_id, "¡Listo! Empecemos de nuevo 😊", page_id)
        return

    send_typing(sender_id, page_id)
    bot_reply = get_response(sender_id, user_text, page_id)
    send_message(sender_id, bot_reply, page_id)


@app.post("/webhook")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
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

            message_id = message.get("mid")
            if message_id in mensajes_procesados:
                print(f"[DUPLICADO] Ignorando mensaje repetido: {message_id}")
                continue
            mensajes_procesados.add(message_id)

            user_text = message["text"].strip()
            print(f"[PÁGINA {page_id}] Usuario {sender_id}: {user_text}")

            background_tasks.add_task(procesar_evento, sender_id, user_text, page_id)

    return {"status": "ok"}