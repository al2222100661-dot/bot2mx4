"""
BOT2MX4 - Messenger multi-cliente
Usa el token correcto según la página que recibe el mensaje.
"""

import requests
import os
from dotenv import load_dotenv
from config.business import get_page_token

load_dotenv()

MESSENGER_API_URL = "https://graph.facebook.com/v19.0/me/messages"


def send_message(recipient_id: str, text: str, page_id: str = "") -> bool:
    token = get_page_token(page_id)
    chunks = split_message(text)

    for chunk in chunks:
        payload = {
            "recipient": {"id": recipient_id},
            "message":   {"text": chunk},
            "messaging_type": "RESPONSE"
        }
        response = requests.post(
            MESSENGER_API_URL,
            params={"access_token": token},
            json=payload
        )
        if response.status_code != 200:
            print(f"[ERROR Messenger] {response.status_code}: {response.text}")
            return False
    return True


def send_typing(recipient_id: str, page_id: str = ""):
    token = get_page_token(page_id)
    payload = {
        "recipient": {"id": recipient_id},
        "sender_action": "typing_on"
    }
    requests.post(
        MESSENGER_API_URL,
        params={"access_token": token},
        json=payload
    )


def split_message(text: str, max_length: int = 1900) -> list:
    if len(text) <= max_length:
        return [text]
    chunks = []
    while len(text) > max_length:
        split_at = text.rfind("\n", 0, max_length)
        if split_at == -1:
            split_at = max_length
        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()
    if text:
        chunks.append(text)
    return chunks
